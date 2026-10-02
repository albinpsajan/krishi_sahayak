"""Build and serialize farmer input checks with weather and price context."""
from datetime import datetime, timezone

from apps.input_guard.models import InputCheck
from apps.input_guard.services.input_price_service import assess_price
from apps.input_guard.services.input_quantity_service import estimate_quantity
from apps.input_guard.services.input_scan_service import validate_image_reference
from apps.input_guard.services.input_suitability_service import assess_suitability
from services.weather_service import DEFAULT_LOCATION, get_weather


KERALA_DISTRICTS = {
    "thiruvananthapuram": (8.5241, 76.9366), "trivandrum": (8.5241, 76.9366),
    "kollam": (8.8932, 76.6141), "pathanamthitta": (9.2648, 76.7870),
    "alappuzha": (9.4981, 76.3388), "alleppey": (9.4981, 76.3388),
    "kottayam": (9.5916, 76.5222), "idukki": (9.8494, 76.9708),
    "ernakulam": (9.9816, 76.2999), "kochi": (9.9312, 76.2673),
    "thrissur": (10.5276, 76.2144), "palakkad": (10.7867, 76.6548),
    "malappuram": (11.0510, 76.0710), "kozhikode": (11.2588, 75.7804),
    "calicut": (11.2588, 75.7804), "wayanad": (11.6854, 76.1320),
    "kannur": (11.8745, 75.3704), "kasaragod": (12.4996, 74.9869),
}


def assess_weather(product_type, farmer):
    profile = getattr(farmer, "farmer_profile", None)
    district = (getattr(profile, "district", "") or "").strip()
    coordinates = KERALA_DISTRICTS.get(district.casefold())
    if not coordinates:
        location_name = f"{district} (weather location not mapped)" if district else "Farm district not set"
        weather = {"location": {"name": location_name}, "rain_chance": None, "wind_kmh": None,
                   "temperature_c": None, "source": "unavailable"}
        return "unavailable", "A weather location is not set for this district. Update your farm profile or check local conditions.", weather
    location_name = f"{district}, Kerala"
    lat, lng = coordinates
    weather = get_weather(lat, lng, location_name)
    rain, wind, temperature = weather.get("rain_chance"), weather.get("wind_kmh"), weather.get("temperature_c")
    required_values = [rain] if product_type in ("Fertilizer", "Pesticide") else []
    if product_type == "Pesticide":
        required_values.extend([wind, temperature])
    if any(value is None for value in required_values) or (rain is None and wind is None and temperature is None):
        return "unavailable", "Live weather is unavailable. Check local rain, wind, and temperature before any weather-sensitive work.", weather
    risks = []
    if rain is not None and rain >= 70 and product_type in ("Fertilizer", "Pesticide"):
        risks.append("Rain is likely; avoid applying before rain.")
    if wind is not None and wind >= 25 and product_type == "Pesticide":
        risks.append("Wind is strong; avoid spraying because of drift risk.")
    if temperature is not None and temperature >= 35 and product_type == "Pesticide":
        risks.append("It is hot; avoid spraying during peak heat.")
    if risks:
        return "caution", " ".join(risks) + " Follow the product label and ask an officer.", weather
    return "no_major_restriction", "Weather data shows no major restriction for this check. Verify conditions at your field and follow the product label.", weather


def assessed_values(farmer, payload):
    image_url = validate_image_reference(payload.image_url, farmer.id)
    suitability_status, suitability_reason = assess_suitability(payload)
    weather_status, weather_note, weather = assess_weather(payload.product_type, farmer)
    price_status, price_note = assess_price(payload.mrp, payload.dealer_price)
    estimate, unit, quantity_note = estimate_quantity(payload.land_area, payload.label_rate_per_acre,
                                                       payload.label_rate_unit, payload.quantity, payload.quantity_unit)
    values = payload.model_dump()
    values.update({
        "image_url": image_url,
        "farmer_id": farmer.id,
        "farmer_name": farmer.full_name,
        "status": "Submitted",
        "suitability_status": suitability_status,
        "suitability_reason": suitability_reason,
        "weather_status": weather_status,
        "weather_note": weather_note,
        "weather_source": weather.get("source", ""),
        "weather_location": weather.get("location", {}).get("name", DEFAULT_LOCATION["name"]),
        "rain_chance": weather.get("rain_chance"),
        "wind_kmh": weather.get("wind_kmh"),
        "temperature_c": weather.get("temperature_c"),
        "price_status": price_status,
        "price_note": price_note,
        "estimated_quantity": estimate,
        "estimated_unit": unit,
        "quantity_note": quantity_note,
    })
    return values


def create_check(db, farmer, payload):
    values = assessed_values(farmer, payload)
    row = InputCheck(**values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_check(db, row, farmer, payload):
    if row.farmer_id != farmer.id:
        raise ValueError("This check belongs to another farmer.")
    if row.status != "More details needed":
        raise ValueError("Only a check returned for more details can be edited and resubmitted.")
    for key, value in assessed_values(farmer, payload).items():
        if key != "farmer_id":
            setattr(row, key, value)
    row.status = "Submitted"
    row.officer_id = None
    row.officer_name = ""
    row.officer_note = ""
    row.reviewed_at = None
    db.commit()
    db.refresh(row)
    return row


def input_check_view(row):
    return {
        "id": row.id, "farmer_id": row.farmer_id, "farmer_name": row.farmer_name,
        "product_name": row.product_name,
        "product_type": row.product_type, "brand": row.brand, "mrp": row.mrp,
        "dealer_price": row.dealer_price, "quantity": row.quantity, "quantity_unit": row.quantity_unit,
        "expiry_date": row.expiry_date.isoformat() if row.expiry_date else None,
        "batch_number": row.batch_number, "dealer_name": row.dealer_name, "crop": row.crop,
        "crop_stage": row.crop_stage, "land_area": row.land_area, "label_crops": row.label_crops,
        "label_rate_per_acre": row.label_rate_per_acre, "label_rate_unit": row.label_rate_unit,
        "notes": row.notes, "image_url": row.image_url, "details_source": "manual_entry",
        "status": row.status, "suitability_status": row.suitability_status,
        "suitability_reason": row.suitability_reason, "weather_status": row.weather_status,
        "weather_note": row.weather_note, "weather_source": row.weather_source,
        "weather_location": row.weather_location,
        "rain_chance": row.rain_chance, "wind_kmh": row.wind_kmh,
        "temperature_c": row.temperature_c, "price_status": row.price_status,
        "price_note": row.price_note, "local_price_range": None,
        "estimated_quantity": row.estimated_quantity, "estimated_unit": row.estimated_unit,
        "quantity_note": row.quantity_note, "officer_id": row.officer_id,
        "officer_name": row.officer_name, "officer_note": row.officer_note,
        "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
        "created_at": row.created_at.replace(tzinfo=timezone.utc).isoformat(),
        "updated_at": row.updated_at.replace(tzinfo=timezone.utc).isoformat(),
    }
