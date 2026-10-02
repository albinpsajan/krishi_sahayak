"""Open-Meteo adapter with a one-minute cache and farmer-safe suggestions."""
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .cache import get, set_value

DEFAULT_LOCATION = {"name": "Palakkad, Kerala", "lat": 10.7867, "lng": 76.6548}

def _suggest(rain, wind, temp):
    if rain >= 70: return "Rain is likely today. Avoid pesticide spraying and check drainage."
    if wind >= 25: return "Wind is strong today. Avoid spraying because coverage may be uneven."
    if temp >= 35: return "It is hot today. Check soil moisture and plan irrigation for the cooler hours."
    return "Conditions look suitable for routine field work. Check the soil before irrigating."

def _fetch(lat, lng):
    query = urlencode({"latitude": lat, "longitude": lng, "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m", "hourly": "precipitation_probability,temperature_2m", "forecast_days": 1, "timezone": "auto"})
    with urlopen(Request(f"https://api.open-meteo.com/v1/forecast?{query}", headers={"User-Agent": "KrishiSahayak/1.0"}), timeout=8) as response:
        raw = json.loads(response.read())
    current = raw.get("current", {}); hourly = raw.get("hourly", {})
    rain = max((v or 0) for v in (hourly.get("precipitation_probability") or [])[:12])
    temp = float(current.get("temperature_2m", 0)); wind = float(current.get("wind_speed_10m", 0))
    return {"location": {"lat": lat, "lng": lng}, "temperature_c": round(temp, 1), "condition": "Rain possible" if rain >= 50 else "Mostly clear", "rain_chance": int(rain), "humidity": int(current.get("relative_humidity_2m", 0)), "wind_kmh": round(wind, 1), "today_forecast": [{"time": t, "temperature_c": v, "rain_chance": p} for t, v, p in zip((hourly.get("time") or [])[:8], (hourly.get("temperature_2m") or [])[:8], (hourly.get("precipitation_probability") or [])[:8])], "action": _suggest(rain, wind, temp), "updated_at": datetime.now(timezone.utc).isoformat(), "source": "Open-Meteo"}

def get_weather(lat, lng, name=None):
    key = f"weather:{round(float(lat), 3)}:{round(float(lng), 3)}"
    cached = get(key)
    if cached: return {**cached, "cached": True}
    try:
        data = _fetch(float(lat), float(lng)); data["location"]["name"] = name or "Your farm"
    except Exception:
        data = {"location": {"name": name or "Your farm", "lat": lat, "lng": lng}, "temperature_c": None, "condition": "Weather temporarily unavailable", "rain_chance": None, "humidity": None, "wind_kmh": None, "today_forecast": [], "action": "Check local conditions before weather-sensitive farm work.", "updated_at": datetime.now(timezone.utc).isoformat(), "source": "fallback", "warning": "Live weather could not be refreshed."}
    return set_value(key, data, 60)
