from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from apps.input_guard.models import InputCheck
from apps.input_guard.services.input_guard_voice_service import reply_for_check, reply_for_open
from apps.farmer_profile.models import User
from core.database import get_db
from core.security import get_current_user
from services.weather_service import DEFAULT_LOCATION, get_weather
from services.market_price_service import get_prices
from services.assistant_intent_service import detect_intent, detect_crop, reply_for

router = APIRouter(prefix="/api", tags=["live data"])

@router.get("/weather/current")
def current_weather(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180), user: User = Depends(get_current_user)):
    return get_weather(lat, lng)

@router.get("/weather/farm/{farmer_id}")
def farmer_weather(farmer_id: int, user: User = Depends(get_current_user)):
    return get_weather(DEFAULT_LOCATION["lat"], DEFAULT_LOCATION["lng"], DEFAULT_LOCATION["name"])

@router.get("/market-prices")
def market_prices(commodity: str = "banana", state: str = "Kerala", district: str = "Thrissur", market: str | None = None, user: User = Depends(get_current_user)):
    return get_prices(commodity, state, district, market)

@router.get("/market-prices/farmer/{farmer_id}")
def farmer_market_prices(farmer_id: int, user: User = Depends(get_current_user)):
    return get_prices()

@router.post("/assistant/query")
def assistant_query(payload: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    intent = detect_intent(payload.get("query", "")); language = payload.get("language", "en")
    if intent == "weather":
        data = get_weather(DEFAULT_LOCATION["lat"], DEFAULT_LOCATION["lng"], DEFAULT_LOCATION["name"])
        reply = data.get("action") or reply_for(intent, language)
    elif intent == "market_price":
        data = get_prices(detect_crop(payload.get("query", ""), payload.get("selected_crop", "banana")))
        if data["available"]:
            reply = (f"{data['commodity']} ({data['variety']}) in {data['market']}: "
                     f"INR {data['modal_price']} per quintal, reported {data['arrival_date']}. "
                     f"{data['warning'] or ''} {data['suggestion']}")
        else:
            reply = data["warning"]
    elif intent.startswith("input_guard"):
        data = {}
        if intent == "input_guard":
            reply = reply_for_open(language)
        else:
            checks = db.query(InputCheck)
            if user.role == "FARMER":
                checks = checks.filter(InputCheck.farmer_id == user.id)
            else:
                checks = checks.filter((InputCheck.officer_id == user.id) | (InputCheck.status.in_(("Submitted", "Under review", "More details needed"))))
            latest = checks.order_by(InputCheck.created_at.desc()).first()
            reply = reply_for_check(intent, latest, language)
            if latest:
                data = {"input_id": latest.id, "status": latest.status,
                        "weather_status": latest.weather_status, "price_status": latest.price_status}
    else:
        data = {}
        reply = reply_for(intent, language)
    return {"success": True, "intent": intent, "reply": reply, "data": data}
