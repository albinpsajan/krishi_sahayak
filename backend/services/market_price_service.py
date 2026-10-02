"""Verified mandi quotes only. Missing observations are never estimated."""
from datetime import datetime, timezone
import math
from .cache import get, set_value
from .market_provider import AGMARKNET_SOURCE, AGMARKNET_SOURCE_URL, fetch_records

SOURCE = AGMARKNET_SOURCE
SOURCE_URL = AGMARKNET_SOURCE_URL
COMMODITIES = {
    "banana": "Banana", "coconut": "Coconut", "paddy": "Paddy(Common)",
    "pepper": "Black pepper", "tomato": "Tomato", "onion": "Onion",
    "potato": "Potato", "arecanut": "Arecanut(Betelnut/Supari)",
    "rubber": "Rubber", "ginger": "Ginger(Green)", "turmeric": "Turmeric",
}


def _normalize(value):
    return str(value).strip().casefold()


def _observation(record, commodity, state, district, market):
    """Validate provider filters locally; keep prices from one dated observation."""
    for field, expected in (("commodity", commodity), ("state", state),
                            ("district", district), ("market", market)):
        if expected and _normalize(record.get(field, "")) != _normalize(expected):
            return None
    try:
        day = datetime.strptime(record["arrival_date"], "%d/%m/%Y").date()
        prices = {name: float(record[name]) for name in ("min_price", "max_price", "modal_price")}
        if not all(math.isfinite(p) and p > 0 for p in prices.values()):
            return None
        if not prices["min_price"] <= prices["modal_price"] <= prices["max_price"]:
            return None
        if day > datetime.now(timezone.utc).date() or not record.get("market"):
            return None
    except (KeyError, ValueError, TypeError):
        return None
    return {**{name: record.get(name, "") for name in
               ("commodity", "state", "district", "market", "variety", "grade")},
            **prices, "arrival_date": day.isoformat(),
            "_source": record.get("_source", SOURCE),
            "_source_url": record.get("_source_url", SOURCE_URL),
            "arrivals": record.get("arrivals")}


def _quotes_for(commodity, state, district=None, market=None):
    records = fetch_records(commodity, state, district, market)
    return [quote for record in records if isinstance(record, dict)
            if (quote := _observation(record, commodity, state, district, market))]


def get_prices(commodity="banana", state="Kerala", district="Thrissur", market=None):
    crop = _normalize(commodity)
    base = {"requested_commodity": crop, "commodity": COMMODITIES.get(crop, commodity),
            "state": state, "district": district, "market": market,
            "available": False, "min_price": None, "max_price": None,
            "modal_price": None, "change": None, "change_direction": None,
            "source": SOURCE, "source_url": SOURCE_URL, "updated_at": None,
            "fetched_at": datetime.now(timezone.utc).isoformat(), "cached": False}
    if crop not in COMMODITIES:
        return {**base, "reason": "unsupported_crop", "warning": "Select a specific supported crop to look up its market price."}
    key = ("verified-market-v1", crop, _normalize(state), _normalize(district), _normalize(market or ""))
    cached = get(key)
    if cached:
        return {**cached, "cached": True}
    try:
        location_match = "market" if market else "district"
        quotes = _quotes_for(COMMODITIES[crop], state, district, market)
        if not quotes and district and not market:
            quotes = _quotes_for(COMMODITIES[crop], state)
            location_match = "state"
    except (OSError, ValueError, TimeoutError):
        # Never expose an upstream URL containing the API credential.
        return {**base, "reason": "provider_unavailable", "warning": "The verified market feed could not be reached. Please retry."}
    if not quotes:
        return {**base, "reason": "no_records", "warning": "No reported price was found for this crop in the selected location."}
    # Newest report, then deterministic market/variety selection. No averaging.
    quotes.sort(key=lambda q: (q["market"], q["variety"], q["grade"]))
    quotes.sort(key=lambda q: q["arrival_date"], reverse=True)
    quote = quotes[0]
    age = (datetime.now(timezone.utc).date() - datetime.fromisoformat(quote["arrival_date"]).date()).days
    warning = "This is an older report; check its date before using the price." if age > 1 else None
    if location_match == "state":
        warning = (f"No recent {district} report was found; showing the latest Kerala mandi quote."
                   if not warning else f"No recent {district} report was found; showing the latest Kerala mandi quote. {warning}")
    result = {**base, **quote, "available": True, "unit": "quintal",
              "source": quote["_source"], "source_url": quote["_source_url"],
              "location_match": location_match, "stale": age > 1, "quotes": quotes,
              "warning": warning,
              "suggestion": "Wholesale mandi report. Confirm variety, quality, buyer quote and transport costs before selling."}
    return set_value(key, result, 60)
