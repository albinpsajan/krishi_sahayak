# KrishiSahayak AI — API Reference

Base URL: `http://127.0.0.1:8000` · Interactive docs: `/docs` (Swagger UI) and `/redoc` · App version: `1.1.0`

**Authentication** — every protected endpoint expects `Authorization: Bearer <token>`. Tokens come from `POST /api/auth/login` or `POST /api/auth/register` and expire after 24 hours.

**Auth column legend**

| Symbol | Meaning |
|---|---|
| — | Public (no token) |
| ✓ | Any authenticated user (`get_current_user`) |
| Farmer | `require_farmer` |
| Officer | `require_officer` |

**Errors** — features that route through `core/errors.py::api_error` return:

```json
{ "detail": { "code": "CASE_NOT_FOUND", "message": "Case not found" } }
```

A few boundary modules (`uploads`, `live data`, `operations`, `community`, `smart planner`) raise plain `HTTPException`s, which FastAPI renders as `{"detail": "<message>"}`. Codes defined in `core/errors.py::AppErrorCode`: `NOT_AUTHENTICATED`, `INVALID_CREDENTIALS`, `EMAIL_ALREADY_REGISTERED`, `USERNAME_ALREADY_TAKEN`, `INVALID_USER_DETAILS`, `MISSING_FARM_PROFILE`, `ACCESS_DENIED`, `CASE_NOT_FOUND`, `CASE_ACCESS_DENIED`, `INVALID_CASE_DATA`, `SCHEME_NOT_FOUND`, `APPLICATION_NOT_FOUND`, `INVALID_APPLICATION_DATA`, `SUBSIDY_MATCHING_ERROR`, `DOCUMENT_REQUIRED`, `AI_SERVICE_UNAVAILABLE`, `FILE_UPLOAD_FAILED`.

---

## Auth — `/api/auth` · `backend/api/auth_routes.py` (farmer_profile)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Create an account (email, username, password, optional role/phone). Returns a JWT. |
| POST | `/api/auth/login` | — | Log in with email **or** username + password. Returns a JWT. |
| PUT | `/api/auth/details` | ✓ | Onboarding step 2: full name, age, role (`FARMER`/`OFFICER`), language. Returns a refreshed JWT. |
| GET | `/api/auth/me` | ✓ | Current user object. |

## Profile — `/api/profile` · `backend/api/profile_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/profile` | ✓ | Account facts plus the role-specific profile (farmer farm record or officer record). |

Farmer farm facts are updated through `PUT /api/operations/profile` (name, phone, district, water source).

## Uploads — `/api` · `backend/api/upload_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/upload` | ✓ | `multipart/form-data` crop photo (`file`). Max 5 MB, JPEG/PNG only (magic-byte validated). Returns `{file_url}`. |
| GET | `/api/uploads/{owner_id}/{filename}` | ✓ | Serve a private crop photo. Owner, officer or admin only; filename must be a stored UUID. |

Files are written to `backend/private_uploads/<user_id>/` and served with `Cache-Control: private, no-store`.

## Crop Cases — `/api/cases` · `backend/api/case_routes.py` (crop_cases)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/cases` | ✓ | Farmers: own cases. Officers/admins: all cases. |
| POST | `/api/cases` | Farmer | Create a case; triggers the preliminary CropDoctor assessment. |
| GET | `/api/cases/{case_id}` | ✓ | Full case record — images, AI assessment, officer review, recommendations. |
| POST | `/api/cases/{case_id}/review` | Officer | Officer verification: confirm or correct the diagnosis, issue the recommendation. |
| PATCH | `/api/cases/{case_id}/status` | ✓ | Change the case status; transitions are validated. |

## Subsidies — `/api/subsidies` · `backend/api/subsidy_routes.py` (subsidies)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/subsidies` | — | Officer-managed scheme directory. |
| POST | `/api/subsidies/apply` | Farmer | Submit an application; deterministic SubsidyChain screening assigns a `risk_level`. |
| GET | `/api/subsidies/applications` | ✓ | Farmers: own applications. Officers/admins: all. |
| POST | `/api/subsidies/applications/{application_id}/decide` | Officer | Approve / Reject / Request information (sole officer authority). |

Risk levels from the rule engine: `LOW_RISK_FAST_TRACK`, `HUMAN_REVIEW_REQUIRED`, `INCOMPLETE_DOCUMENTS`. The engine never auto-approves or auto-rejects.

## Officer — `/api/officer` · `backend/api/officer_routes.py` (autoclerk)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/officer/autoclerk/{case_id}` | Officer | Generated official administrative report (markdown) for a case. |

Farmer facts in the report are read through `profile_service.get_farmer_context()` — the single source of truth.

## Audit — `/api/audit` · `backend/api/audit_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/audit/ledger` | ✓ | Full hash-chained audit timeline (oldest first). |
| GET | `/api/audit/verify` | — | Re-walks the SHA-256 chain; returns `VALID` or `TAMPERED` with the corrupted entry id. |

## Notifications — `/api/notifications` · `backend/api/notification_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications` | ✓ | Own notifications (English + Malayalam). |
| PUT | `/api/notifications/{notification_id}/read` | ✓ | Mark one notification as read. |

## Farm operations — `/api/operations` · `backend/api/operation_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/operations/plots` | ✓ | Own plots with the latest crop record, growth stage and planting date. |
| POST | `/api/operations/plots` | Farmer | Create a plot and its first crop season. Future planting dates are rejected (422). |
| PUT | `/api/operations/profile` | Farmer | Update name, phone, district and water source. |
| GET | `/api/operations/resources` | ✓ | Shared resource catalogue (machinery, transport, irrigation, labour). |
| GET | `/api/operations/bookings` | ✓ | Farmers: own bookings. Officers/admins: all. |
| POST | `/api/operations/bookings` | Farmer | Request a slot. `request_key` makes retries idempotent (409 on a conflicting key). |
| PATCH | `/api/operations/bookings/{booking_id}` | ✓ | Advance a booking through its status flow. |
| GET | `/api/operations/groups` | ✓ | Cooperation groups with member count, join state and activity history. |
| POST | `/api/operations/groups` | Farmer | Open a cooperation group; the organiser joins automatically. |
| POST | `/api/operations/groups/{group_id}/join` | Farmer | Join a group that is still gathering interest. |
| PATCH | `/api/operations/groups/{group_id}` | Officer | Move a group to the next stage only (`Gathering interest → Coordinating → Scheduled → Completed`). |
| GET | `/api/operations/cashbook` | ✓ | Own cashbook entries, newest first. |
| POST | `/api/operations/cashbook` | Farmer | Add an income or expense entry. |
| GET | `/api/operations/documents` | ✓ | Names of documents the farmer has ticked off. |
| PUT | `/api/operations/documents/{name}` | Farmer | Toggle one of: Identity proof, Land record, Bank details, Crop insurance, Application receipt. |

Booking and group mutations are appended to the audit ledger through `apps/operations/service.record()`.

## Community board — `/api/community` · `backend/api/community_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/community` | ✓ | Published posts; officers/admins also see unpublished ones, and every user sees their own drafts. |
| POST | `/api/community` | ✓ | Create a post on a board (Paddy, Banana, Coconut, Pepper, Machinery, Market, Schemes). Label is `Expert notice` for officers/admins, otherwise `Farmer experience`. |
| PATCH | `/api/community/{post_id}` | Officer | Set status to `Published` or `Not published`. |

**Moderation is not agronomic verification** — publishing a post says nothing about the correctness of its content.

## Smart Planner — `/api/smart-planner` · `backend/apps/smart_planner/routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/smart-planner/rules` | — | Planner constants: 7.5 m × 7.5 m coconut spacing, 2 m boundary buffer, water sources, irrigation methods. |
| POST | `/api/smart-planner/plots` | Farmer | Save a plot from a WGS84 GeoJSON boundary or a local boundary; stores area in m², acres, cents and hectares. |
| GET | `/api/smart-planner/plots` | ✓ | Own plots, newest first. |
| GET | `/api/smart-planner/plots/{plot_id}` | ✓ | Plot detail. Owner, officer or admin (404 otherwise, to avoid leaking existence). |
| POST | `/api/smart-planner/plans/generate` | Farmer | Generate a plan from a plot plus crop, water source, soil, budget, irrigation, plantation type and coconut age. |
| GET | `/api/smart-planner/plans` | ✓ | Farmers: own plans (without the plan JSON). Officers/admins: all. |
| GET | `/api/smart-planner/plans/{plan_id}` | ✓ | Plan detail including the full plan JSON. |
| POST | `/api/smart-planner/plans/{plan_id}/request-review` | Farmer | Send a `Generated` or `Changes Requested` plan to an officer and notify the farmer. |
| GET | `/api/smart-planner/officer/pending` | Officer | Plans in `Sent for Review` or `Under Review`. |
| PATCH | `/api/smart-planner/plans/{plan_id}/review` | Officer | Record the review decision and notify the farmer. |
| POST | `/api/smart-planner/locations` | Farmer | Save a farm location (latitude, longitude, accuracy, source). |
| GET | `/api/smart-planner/plans/{plan_id}/versions` | ✓ | Full version history with each version's layout data. |
| POST | `/api/smart-planner/plans/{plan_id}/customize` | Farmer | Apply a change, store a new `PlanVersion` and a `PlanChangeRequest`, and move the plan to `Sent for Review`. |

All geometry and layout numbers come from deterministic rules in `apps/smart_planner/services.py` — no model inference.

## Live data & assistant — `/api` · `backend/api/live_data_routes.py`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/weather/current?lat=&lng=` | ✓ | Current weather from Open-Meteo (lat −90..90, lng −180..180). Cached 60 s. |
| GET | `/api/weather/farm/{farmer_id}` | ✓ | Weather for the default pilot location (Palakkad, Kerala — 10.7867, 76.6548). |
| GET | `/api/market-prices?commodity=&state=&district=&market=` | ✓ | Commodity prices. Defaults: `banana`, `Kerala`, `Thrissur`. Returns clearly labelled pilot fallback data. |
| GET | `/api/market-prices/farmer/{farmer_id}` | ✓ | Default market snapshot for the farmer's workspace. |
| POST | `/api/assistant/query` | ✓ | Body `{query, language, selected_crop?}`. Returns `{success, intent, reply, data}`; `intent` drives whether live data is attached. |

Supported intents include `weather` and `market_price` (both return live data); everything else returns a templated reply in the requested language.

---

## Static mounts

| Path | Source | Notes |
|---|---|---|
| `/uploads` | `assets/` | Only mounted if the directory exists at startup. |
| `/assets` | `frontend/dist/assets/`, falling back to `assets/` | Mounted so the built SPA's hashed bundles resolve. |
| `/` | `frontend/dist/index.html` | Served when a build exists; otherwise returns the API banner JSON. |

## Future: irrigation — `/api/farms` (planned)

`apps/farms/models.py` defines `Farm`, `FarmCrop`, `IrrigationPlan`, `IrrigationComponent` and `IrrigationOfficerReview`. `Farm`/`FarmCrop` are already used by the live farm-operations feature; the irrigation plan engine and its router are the next feature branch. See [`features/irrigation.md`](features/irrigation.md).
