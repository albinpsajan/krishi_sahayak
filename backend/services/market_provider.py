"""HTTP adapters for official AGMARKNET market-price feeds."""
from datetime import date
from functools import lru_cache
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DATA_GOV_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_SOURCE = "AGMARKNET via data.gov.in"
DATA_GOV_SOURCE_URL = "https://www.data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi"
AGMARKNET_BASE = "https://api.agmarknet.gov.in/v1"
AGMARKNET_SOURCE = "AGMARKNET live portal"
AGMARKNET_SOURCE_URL = "https://agmarknet.gov.in/"
PAGE_SIZE = 1000

AGMARKNET_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KrishiSahayak/1.0",
}

STATE_ALIASES = {"kerala": {"kerala", "keralam"}}
DISTRICT_ALIASES = {
    "thrissur": {"thrissur", "thirssur"},
    "palakkad": {"palakkad", "palakad"},
}
DISTRICT_DISPLAY = {"thirssur": "Thrissur", "palakad": "Palakkad"}
STATE_DISPLAY = {"keralam": "Kerala"}


def _normalize(value):
    return str(value or "").strip().casefold()


def _accepted_names(value, aliases):
    normalized = _normalize(value)
    return aliases.get(normalized, {normalized})


def _request_json(url, *, method="GET", payload=None, headers=None, timeout=12):
    request_headers = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    with urlopen(Request(url, data=data, method=method, headers=request_headers), timeout=timeout) as response:
        return json.load(response)


@lru_cache(maxsize=1)
def _agmarknet_filters():
    payload = _request_json(f"{AGMARKNET_BASE}/daily-price-arrival/filters",
                            headers=AGMARKNET_HEADERS, timeout=15)
    data = payload.get("data") if isinstance(payload, dict) else None
    required = ("cmdt_data", "state_data", "district_data", "market_data")
    if not isinstance(data, dict) or any(not isinstance(data.get(key), list) for key in required):
        raise ValueError("Invalid AGMARKNET filter response")
    return data


def _resolve_named_id(rows, name_field, requested, aliases=None):
    accepted = _accepted_names(requested, aliases or {})
    for row in rows:
        if _normalize(row.get(name_field)) in accepted:
            return row
    for row in rows:
        actual = _normalize(row.get(name_field))
        if any(name and (name in actual or actual in name) for name in accepted):
            return row
    return None


def _display_state(name):
    return STATE_DISPLAY.get(_normalize(name), name)


def _display_district(name):
    return DISTRICT_DISPLAY.get(_normalize(name), name)


def _month_windows(today=None, count=3):
    current = today or date.today()
    year, month = current.year, current.month
    for _ in range(count):
        yield year, month
        month -= 1
        if month == 0:
            month = 12
            year -= 1


def _fetch_agmarknet_month(state_id, commodity_id, year, month):
    query = urlencode({
        "year": year,
        "month": month,
        "stateId": state_id,
        "commodityId": commodity_id,
        "includeExcel": "false",
    })
    return _request_json(f"{AGMARKNET_BASE}/prices-and-arrivals/date-wise/specific-commodity?{query}",
                         headers=AGMARKNET_HEADERS, timeout=20)


def _records_from_agmarknet_payload(payload, filters, commodity, state_row, district_ids, market):
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return []
    market_lookup = {_normalize(row.get("mkt_name")): row for row in filters["market_data"]
                     if row.get("state_id") == state_row["state_id"]}
    district_lookup = {row["id"]: row for row in filters["district_data"]
                       if row.get("state_id") == state_row["state_id"]}
    requested_market = _normalize(market)
    records = []
    for market_report in payload.get("markets") or []:
        market_name = market_report.get("marketName", "")
        market_row = market_lookup.get(_normalize(market_name), {})
        actual_market = market_row.get("mkt_name") or market_name
        if requested_market and requested_market != _normalize(actual_market):
            continue
        district_id = market_row.get("district_id")
        if district_ids is not None and district_id not in district_ids:
            continue
        district_row = district_lookup.get(district_id, {})
        district_name = _display_district(district_row.get("district_name", ""))
        for day in market_report.get("dates") or []:
            arrival_date = day.get("arrivalDate")
            for quote in day.get("data") or []:
                records.append({
                    "commodity": commodity,
                    "state": _display_state(state_row["state_name"]),
                    "district": district_name,
                    "market": actual_market.strip(),
                    "variety": quote.get("variety", ""),
                    "grade": quote.get("grade", ""),
                    "arrival_date": arrival_date,
                    "min_price": quote.get("minimumPrice"),
                    "max_price": quote.get("maximumPrice"),
                    "modal_price": quote.get("modalPrice"),
                    "arrivals": quote.get("arrivals"),
                    "_source": AGMARKNET_SOURCE,
                    "_source_url": AGMARKNET_SOURCE_URL,
                })
    return records


def _fetch_agmarknet_records(commodity, state, district=None, market=None):
    filters = _agmarknet_filters()
    commodity_row = _resolve_named_id(filters["cmdt_data"], "cmdt_name", commodity)
    state_row = _resolve_named_id(filters["state_data"], "state_name", state, STATE_ALIASES)
    if not commodity_row or not state_row:
        return []
    district_ids = None
    if district:
        district_ids = {row["id"] for row in filters["district_data"]
                        if row.get("state_id") == state_row["state_id"]
                        and _normalize(row.get("district_name")) in _accepted_names(district, DISTRICT_ALIASES)}
        if not district_ids:
            return []
    records = []
    for year, month in _month_windows():
        payload = _fetch_agmarknet_month(state_row["state_id"], commodity_row["cmdt_id"], year, month)
        records = _records_from_agmarknet_payload(payload, filters, commodity_row["cmdt_name"],
                                                  state_row, district_ids, market)
        if records:
            return records
    return records


def _fetch_data_gov_records(commodity, state, district=None, market=None):
    api_key = os.getenv("DATA_GOV_API_KEY", "").strip()
    if not api_key:
        return []
    params = {"api-key": api_key, "format": "json", "limit": PAGE_SIZE,
              "filters[commodity]": commodity, "sort[arrival_date]": "desc"}
    for field, value in (("state", state), ("district", district), ("market", market)):
        if value:
            params[f"filters[{field}]"] = value.strip()
    records = []
    for offset in range(0, 10000, PAGE_SIZE):
        params["offset"] = offset
        payload = _request_json(f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}?{urlencode(params)}",
                                headers={"Accept": "application/json", "User-Agent": "KrishiSahayak/1.0"},
                                timeout=12)
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            raise ValueError("Invalid market feed response")
        page = [{**record, "_source": DATA_GOV_SOURCE, "_source_url": DATA_GOV_SOURCE_URL}
                for record in payload["records"]]
        records.extend(page)
        if len(page) < PAGE_SIZE or len(records) >= int(payload.get("total", len(records))):
            return records
    raise ValueError("Market query too broad; select a district or market")


def fetch_records(commodity, state, district=None, market=None):
    """Return official mandi records. Primary source is the keyless AGMARKNET portal."""
    try:
        records = _fetch_agmarknet_records(commodity, state, district, market)
        if records:
            return records
    except (OSError, ValueError, TimeoutError):
        if not os.getenv("DATA_GOV_API_KEY", "").strip():
            raise
    return _fetch_data_gov_records(commodity, state, district, market)
