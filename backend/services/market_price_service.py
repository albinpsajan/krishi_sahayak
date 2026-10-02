"""Market-price adapter. Uses a safe local fallback until a state feed is configured."""
from datetime import datetime, timezone
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .cache import get, set_value

FALLBACK = {"banana": {"commodity": "Banana", "market": "Thrissur", "state": "Kerala", "district": "Thrissur", "min_price": 2800, "max_price": 3400, "modal_price": 3100}, "coconut": {"commodity": "Coconut", "market": "Palakkad", "state": "Kerala", "district": "Palakkad", "min_price": 7600, "max_price": 8800, "modal_price": 8200}, "paddy": {"commodity": "Paddy", "market": "Palakkad", "state": "Kerala", "district": "Palakkad", "min_price": 2200, "max_price": 2600, "modal_price": 2400}, "pepper": {"commodity": "Pepper", "market": "Wayanad", "state": "Kerala", "district": "Wayanad", "min_price": 54000, "max_price": 62000, "modal_price": 58000}, "tomato": {"commodity": "Tomato", "market": "Thrissur", "state": "Kerala", "district": "Thrissur", "min_price": 1800, "max_price": 2600, "modal_price": 2200}, "onion": {"commodity": "Onion", "market": "Kochi", "state": "Kerala", "district": "Ernakulam", "min_price": 2400, "max_price": 3200, "modal_price": 2800}, "potato": {"commodity": "Potato", "market": "Kochi", "state": "Kerala", "district": "Ernakulam", "min_price": 2100, "max_price": 2900, "modal_price": 2500}, "arecanut": {"commodity": "Arecanut", "market": "Kasaragod", "state": "Kerala", "district": "Kasaragod", "min_price": 30000, "max_price": 38000, "modal_price": 34000}, "rubber": {"commodity": "Rubber", "market": "Kottayam", "state": "Kerala", "district": "Kottayam", "min_price": 16500, "max_price": 18500, "modal_price": 17500}, "ginger": {"commodity": "Ginger", "market": "Kozhikode", "state": "Kerala", "district": "Kozhikode", "min_price": 6500, "max_price": 8500, "modal_price": 7500}, "turmeric": {"commodity": "Turmeric", "market": "Palakkad", "state": "Kerala", "district": "Palakkad", "min_price": 7200, "max_price": 9000, "modal_price": 8100}, "vegetables": {"commodity": "Vegetables", "market": "Thrissur", "state": "Kerala", "district": "Thrissur", "min_price": 2200, "max_price": 3200, "modal_price": 2700}}

def _suggest(change):
    if change > 0: return "Price has improved. If transport is available, compare buyers or consider group selling."
    if change < 0: return "Price has softened. Check storage, quality and more than one buyer before selling."
    return "Compare at least two buyers and confirm transport costs before selling."

def get_prices(commodity="banana", state="Kerala", district="Thrissur", market=None):
    key = f"market:{commodity.lower()}:{state.lower()}:{district.lower()}:{(market or '').lower()}"
    cached = get(key)
    if cached: return {**cached, "cached": True}
    item = dict(FALLBACK.get(commodity.lower(), FALLBACK["banana"])); item.update({"commodity": commodity.title(), "state": state, "district": district, "market": market or item["market"]})
    previous = get(f"market-previous:{key}") or item["modal_price"] - 150
    item["change"] = item["modal_price"] - previous; item["change_direction"] = "up" if item["change"] > 0 else "down" if item["change"] < 0 else "flat"; item["suggestion"] = _suggest(item["change"]); item["updated_at"] = datetime.now(timezone.utc).isoformat(); item["source"] = "pilot fallback"; item["warning"] = "Using pilot reference data; connect a verified market feed before production decisions."
    set_value(f"market-previous:{key}", item["modal_price"], 86400)
    return set_value(key, item, 60)
