# Live Field Signals & Assistant

## Purpose
Give the farmer the three things that change hour to hour — weather, market price and a way to ask about them in their own language — without a page reload and without the AI inventing any number.

> **Labelling rule.** Weather comes from a live public source and is labelled `source: "Open-Meteo"`. Market prices come only from official AGMARKNET sources: the public AGMARKNET portal API first, then data.gov.in only when `DATA_GOV_API_KEY` is configured. Feed failures and missing records return `available: false` with null prices. No price or trend is synthesized.

## Inputs
- Weather: `lat` (−90..90) and `lng` (−180..180); the farmer-default variant uses the saved farm location or `DEFAULT_LOCATION` (Palakkad, Kerala — 10.7867, 76.6548).
- Market prices: `commodity` (default `banana`), `state` (default `Kerala`), `district` (default `Thrissur`), optional `market`.
- Assistant: `{query, language (default "en"), selected_crop}` from voice or typed input.

## Outputs
- **Weather** — temperature °C, condition (`Rain possible` / `Mostly clear`), rain chance %, humidity, wind km/h, an 8-hour forecast strip, a field `action` suggestion, `updated_at`, `source`, and `cached` on repeat reads.
- **Market prices** — `available`, requested crop, actual commodity/market/district/variety/grade, min/max/modal wholesale prices per quintal, `arrival_date` (report date), `fetched_at` (retrieval time), source link, `location_match`, and stale-report warning. Changes are null because no comparable historical series is provided.
- **Assistant** — `{success, intent, reply, data}`. `weather` and `market_price` attach live data; every other intent returns a language-matched templated reply with no data.

## Main files
| File | Responsibility |
|---|---|
| `services/weather_service.py` | Open-Meteo adapter, farmer-safe suggestion thresholds |
| `services/market_provider.py` | Official AGMARKNET portal and optional data.gov.in HTTP adapters |
| `services/market_price_service.py` | Crop aliases, validation, dated observation selection and crop/location cache |
| `services/assistant_intent_service.py` | Keyword intent detection, crop detection, multilingual replies |
| `services/cache.py` | 60-second in-process cache shared by both adapters |
| `api/live_data_routes.py` | Authenticated HTTP boundary |
| `frontend/src/components/weather/` | `WeatherCard.jsx`, `WeatherActionSuggestion.jsx` |
| `frontend/src/components/market/` | `MarketPriceCard.jsx`, `PriceChangeBadge.jsx` |
| `frontend/src/components/voice/` | `VoiceAssistantButton.jsx`, `VoiceAssistantPanel.jsx` |
| `frontend/src/services/liveDataApi.js` | API client for this feature |
| `frontend/src/services/voiceAssistantService.js` | Web Speech API wrapper |
| `frontend/src/hooks/useAutoRefresh.js` | 60-second polling; keeps the last good response on failure |

## Database models
None. This feature is stateless — no farmer data is stored, and location comes from `POST /api/smart-planner/locations`.

## API endpoints
`GET /api/weather/current` · `GET /api/weather/farm/{farmer_id}` · `GET /api/market-prices` · `GET /api/market-prices/farmer/{farmer_id}` · `POST /api/assistant/query`. All require a token.

## Deterministic rules (nothing here is a model)
- **Weather thresholds** — rain chance ≥ 70 % → avoid spraying, check drainage; wind ≥ 25 km/h → avoid spraying, coverage may be uneven; temperature ≥ 35 °C → check soil moisture, irrigate in cooler hours; otherwise conditions suit routine field work.
- **Price advice** — change > 0 → compare buyers or consider group selling; change < 0 → check storage, quality and more than one buyer; flat → compare at least two buyers and confirm transport.
- **Intent detection** — first keyword hit wins over an ordered dictionary covering `weather`, `market_price`, `planner`, `resource`, `crop_report`, `scheme`, `documents`, with English, Malayalam, Hindi and Tamil keywords; no match → `help`.
- **Crop detection** — banana, coconut, paddy, pepper, tomato (English + Hindi/Tamil), defaulting to the caller's `selected_crop` or banana.
- **Price change** — no trend badge is shown without a verified comparable historical series.

## AI components
None. There is no model in this feature. The "assistant" is keyword routing plus multilingual templates — deliberately, so a voice query can never produce an unsourced number.

## Dependencies
`farmer_profile` (auth only), `core.security`, `core.logging_config`. No other feature depends on this one.

## Known limitations
- **No market key is required for the primary feed.** `DATA_GOV_API_KEY` is optional and used only as a secondary official source. A `.env` file is not loaded automatically, so export the key before `python run_app.py` only when you want the data.gov.in fallback.
- The UI currently queries Thrissur, Kerala first. If that district has no recent report for a crop, the backend may show the latest Kerala mandi quote with `location_match: "state"` and the actual market/district in the payload.
- `services/market_provider.py` owns HTTP access; `services/market_price_service.py` validates crop/location, handles district-to-state fallback and selects the newest report. `hooks/useMarketPrices.js` handles independent refresh and ignores obsolete responses after crop switches.
- **Weather is current-conditions only** — no forecast beyond 8 hours, no rainfall totals, no station-level accuracy note.
- `urlopen` is called synchronously inside a `def` (not `async def`) endpoint with an 8-second timeout, so a slow provider holds a worker thread.
- Cache is per-process and in-memory, so it does not survive a restart and is not shared across workers.
- The pilot default location is hard-coded to Palakkad for `weather/farm/{id}`; a real per-farmer geolocation is not wired in.
- `GET /api/weather/farm/{farmer_id}` and `GET /api/market-prices/farmer/{farmer_id}` accept any id and return defaults — they do not enforce ownership, so they must not be trusted to identify a farmer.
- Assistant replies are templated, not conversational; unknown phrasing falls back to a fixed help line.
- Voice input depends on the browser Web Speech API, which is unavailable in some browsers and in some languages — the typed input is the real fallback.

## How to test
`tests/test_market_prices.py` covers separate crop caches, crop/location validation, state fallback, feed failures, malformed observations, report dates and AGMARKNET payload normalization. `tests/test_live_data.py` covers assistant routing. Tests use fixtures only at the mocked provider boundary; production has no fixture price fallback.
