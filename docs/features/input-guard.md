# Input Guard

Input Guard keeps farmer-entered product details, price checks, weather context, label-rate planning estimates, and officer decisions in one workflow.

## Request flow

1. A farmer optionally uploads one JPEG, PNG, or WebP photo to `POST /api/input-guard/upload`. Files are size limited to 5 MB and stored outside the public static directory. The returned authenticated image URL is attached to the next check.
2. `POST /api/input-guard/check` validates and saves the farmer's manual entry. The orchestration service reads live weather through `services/weather_service.py` and calls the suitability, price, and quantity rules before saving the snapshot.
3. `GET /api/input-guard` returns only the current farmer's records. `GET /api/input-guard/officer/pending` is restricted to authorized officers and administrators.
4. `PATCH /api/input-guard/officer/{id}/review` saves an officer decision and note. The farmer sees that decision and note on the same check.
5. When the officer requests more details, the farmer can edit and resubmit that same check with `PATCH /api/input-guard/{id}`. Other submitted/final checks cannot be edited through this route.

## Code map

- `backend/apps/input_guard/models.py`: persisted check and review fields.
- `backend/apps/input_guard/schemas.py`: request validation.
- `backend/apps/input_guard/services/input_guard_service.py`: assessment orchestration and API view serialization.
- `backend/apps/input_guard/services/input_scan_service.py`: validates uploaded photo references. The MVP does not run OCR.
- `backend/apps/input_guard/services/input_suitability_service.py`: conservative checks based on manually entered expiry and label crop details.
- `backend/apps/input_guard/services/input_price_service.py`: compares the dealer quote with the entered printed MRP; no local price range is fabricated.
- `backend/apps/input_guard/services/input_quantity_service.py`: computes a planning quantity only from a per-acre rate the farmer copied from the package.
- `backend/apps/input_guard/services/input_verification_service.py`: officer review state transitions.
- `backend/apps/input_guard/services/input_guard_voice_service.py`: localized latest-check, weather-warning, and officer-note voice replies.
- `backend/apps/input_guard/routes.py`: authenticated upload, farmer, and officer endpoints.
- `frontend/src/pages/InputGuardPage.jsx`: farmer check form, result/history view, and officer queue.
- `frontend/src/i18n/inputGuardTranslations.js`: visible feature copy for English, Malayalam, Hindi, and Tamil.
- `frontend/src/inputGuard.css`: Input Guard layout plus shared visual tokens and responsive rules.

## Safety limits

- A photo is stored for the farmer and authorized officer; the MVP does not claim to extract or verify label text.
- Product originality is never asserted.
- Crop suitability remains “needs verification” unless the manually entered expiry has passed or manually entered crop-label details conflict. Even matching label text does not replace officer review.
- Quantity estimates are omitted unless the farmer enters a rate printed on the package. The UI labels the result as a planning amount and asks the farmer to confirm it.
- Price checks compare only the entered MRP with the dealer quote. Local cooperative and mandi input prices are not connected.
- Weather comes from the existing Open-Meteo adapter. If it is unavailable, the result says so and asks the farmer to check field conditions.
- Officer approval records the officer's decision for this check; the app does not issue pesticide dosage directions.
