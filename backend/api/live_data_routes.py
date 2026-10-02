from fastapi import APIRouter, Depends, Query
from apps.farmer_profile.models import User
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
def assistant_query(payload: dict, user: User = Depends(get_current_user)):
    intent = detect_intent(payload.get("query", "")); language = payload.get("language", "en")
    if intent == "weather":
        data = get_weather(DEFAULT_LOCATION["lat"], DEFAULT_LOCATION["lng"], DEFAULT_LOCATION["name"])
        reply = data.get("action") or reply_for(intent, language)
    elif intent == "market_price":
        data = get_prices(detect_crop(payload.get("query", ""), payload.get("selected_crop", "banana")))
        reply = f"{data['commodity']} modal price in {data['market']} is ₹{data['modal_price']} per quintal. {data['suggestion']}"
    else:
        data = {}
        reply = reply_for(intent, language)
    return {"success": True, "intent": intent, "reply": reply, "data": data}
