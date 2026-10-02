# KrishiSahayak AI — Architecture & Maintainability

> **Core Development Principle:** a new developer can enter the project, identify a feature, trace its data flow, locate the responsible file, reproduce the bug, and fix it without needing to understand the entire codebase.

## 1. Feature-based separation

Each major functionality lives in its own package. Nothing is a single large file.

- Backend features: `backend/apps/<feature>/` — models, schemas, services per feature.
- Backend API: `backend/api/<feature>_routes.py` — one router per feature (`smart_planner` is the one exception; its routes live next to its models inside the feature package).
- Shared, non-domain helpers: `backend/services/` (weather, market price, assistant intent, plan customization, cache).
- Frontend: `pages/`, `components/`, `layouts/`, `hooks/`, `services/`, `i18n/`, `utils/`.

Feature packages in the repository: `farmer_profile`, `crop_cases`, `subsidies`, `audit`, `notifications`, `autoclerk`, `operations`, `community`, `smart_planner`, `farms` (foundation only).

## 2. Subsidy module is self-contained

`backend/apps/subsidies/` mixes with nothing:

```
apps/subsidies/
├── models.py                 # SubsidyScheme, SubsidyApplication, ApplicationDocument
├── schemas.py
├── services/
│   ├── subsidy_matcher.py    # orchestrates screening -> risk level
│   ├── eligibility_checker.py# deterministic rules (pure functions)
│   └── document_checker.py   # missing-document detection (pure functions)
```

Debug map:

| Symptom | File to open |
|---|---|
| Wrong subsidy match / risk level | `services/subsidy_matcher.py` |
| Wrong eligibility verdict | `services/eligibility_checker.py` |
| Wrong missing-document list | `services/document_checker.py` |
| Wrong application prefill/data | `api/subsidy_routes.py` |
| Wrong deadline/scheme facts | `models.py` (officer-managed data) |

## 3. AI never controls business rules

```
Officer-managed scheme database
        ↓
  Eligibility rules (apps/subsidies/services/ — deterministic)
        ↓
  Deterministic matcher (risk screening)
        ↓
  AI explanation (backend/ai/ — CropDoctor)
        ↓
  Farmer / Officer interface
```

The AI layer (`backend/ai/`) **explains and assists only**. It never invents subsidy amounts, eligibility conditions, government rules, deadlines, required documents, or application links. Every AI diagnosis is stored as *preliminary* and is superseded by the officer review.

## 4. One responsibility per file

No `subsidyEverything.py`. Each module states its responsibility in its docstring; if two responsibilities share a file, split it.

## 5. Reusable services (one source of truth)

Farmer name, phone, land size, crops and district are owned by `apps/farmer_profile/`. Every other feature reads them through `profile_service.get_farmer_context()` — never by duplicating copies:

```
Farmer Profile → profile_service → Subsidies / Crop Cases / AutoClerk
```

## 6. API separation

Each prefix is served by exactly one router file. The full endpoint list is in [`api.md`](api.md).

```
/api/auth            → api/auth_routes.py
/api/profile         → api/profile_routes.py
/api/upload(s)       → api/upload_routes.py
/api/cases           → api/case_routes.py
/api/subsidies       → api/subsidy_routes.py
/api/officer         → api/officer_routes.py
/api/audit           → api/audit_routes.py
/api/notifications   → api/notification_routes.py
/api/operations      → api/operation_routes.py
/api/community       → api/community_routes.py
/api/smart-planner   → apps/smart_planner/routes.py
/api/weather, /api/market-prices, /api/assistant
                    → api/live_data_routes.py
```

Cross-feature reads never happen inside a router: a router authenticates, validates with Pydantic, delegates to a service, and serialises the result. A feature that needs another feature's data calls that feature's service (`profile_service`, `notification_service`, `plan_customization_service`).

`backend/main.py` stays a thin factory — it creates tables, runs lightweight migrations, seeds, mounts static files and includes the routers. No endpoint logic lives there.

## 7. Environment & secrets

All secrets come from environment variables via `backend/config/settings.py` (see `.env.example`). `.env` is gitignored; only `.env.example` with placeholders is committed. No API key, password or secret is hard-coded.

Supported variables: `JWT_SECRET_KEY`, `KRISHI_DB_PATH`, `DATABASE_URL`, `CROP_DOCTOR_API_KEY`, `CORS_ORIGINS`, `PORT`, `KRISHI_RELOAD`.

The settings module reads `os.environ` only — it does not parse a `.env` file. Export the values (shell, process manager, container env) before starting the app. The only in-code secret is the JWT fallback, which exists so the local demo runs out of the box and **must** be overridden in production.

## 8. Error handling

All feature errors go through `core/errors.py::api_error(status, code, message)` producing:

```json
{ "detail": { "code": "SCHEME_NOT_FOUND", "message": "Subsidy scheme not found" } }
```

Codes: `MISSING_FARM_PROFILE`, `SCHEME_NOT_FOUND`, `DOCUMENT_REQUIRED`, `INVALID_APPLICATION_DATA`, `SUBSIDY_MATCHING_ERROR`, `AI_SERVICE_UNAVAILABLE`, `CASE_NOT_FOUND`, `ACCESS_DENIED`, … The user sees the simple message; developers get the code and logs.

New features should adopt the same envelope. Where a boundary module still raises a plain `HTTPException` (`uploads`, `live data`, `operations`, `community`, `smart planner`), the response is `{"detail": "<message>"}` — migrate those to `api_error` when the feature is next touched rather than sprinkling one-off formats.

## 9. Logging

`core/logging_config.py` provides feature-tagged log lines:

```
[SUBSIDY_MATCH] score=100 risk=LOW_RISK_FAST_TRACK rules_passed=3 flags=0 missing_docs=0
[CROP_CASE] created case_number=CASE-2026-1234 farmer_id=1 crop=Paddy
[SUBSIDY_DECISION] application=SUB-2026-56789 officer_id=2 decision=Approved
```

Logs contain identifiers only — never phone numbers, addresses, document contents or tokens.

## 10. Testing

`tests/` mirrors the features:

```
tests/
├── test_environment.py       # Shared bootstrap: sys.path + isolated temp database
├── test_live_data.py         # Weather / market-price services
├── test_workflows.py         # End-to-end workflows across features
├── ai/test_crop_doctor.py    # AI output contract
├── audit/test_audit_ledger.py# Tamper detection
├── autoclerk/                # Report generation
├── farmer_profile/           # Auth security + profile service
├── smart_planner/            # Geometry and layout rules
└── subsidies/                # Matching, eligibility, documents
```

Run: `python -m unittest discover -s tests -t . -v`

Covered cases include: eligible farmer, ineligible farmer, missing documents, large landholding, unverified case, tampered ledger, unknown crop, wrong-secret token.

Tests use an isolated temp database (`KRISHI_DB_PATH` is redirected by `tests/test_environment.py`), never the developer's real data. The redirection happens **before** any backend import, so importing a backend module never resolves the real database path.

## 11. Documentation

Every feature has `docs/features/<feature>.md` with: purpose, inputs, outputs, main files, database models, API endpoints, AI components, dependencies, known limitations, how to test. Feature pages live in `docs/features/`: `farmer-profile`, `crop-cases`, `subsidies`, `audit`, `notifications`, `autoclerk`, `operations`, `community`, `smart-planner`, `live-data`, `irrigation` (planned).

## 12. Naming

Files and functions are descriptive: `subsidy_matcher.py`, `eligibility_checker.py`, `document_checker.py`, `notification_service.py`; `match_farmer_with_subsidies()`, `evaluate_subsidy_application()`, `find_missing_documents()`, `verify_ledger_integrity()`.

## 13. No unnecessary duplication

Cross-feature reads go through services (`profile_service`, `notification_service`) instead of copying rows or logic. One source of truth → multiple features.

## 14. Change isolation

Changing subsidy eligibility touches `apps/subsidies/` only. Irrigation, documents and profile code are untouched. The farms/irrigation feature is a separate package that can grow without affecting live features.

One documented exception: `apps/operations/` writes `Farm` and `FarmCrop` rows from `apps/farms/models.py`, because plots and crop seasons are a live feature today. `Farm`/`FarmCrop` are therefore shared models, while the `Irrigation*` models remain private to the future irrigation feature.

## 14b. Frontend conventions

- One file per screen in `src/pages/`; reusable UI in `src/components/` (`ui/` primitives, plus `market/`, `weather/`, `voice/`, `smartPlanner/`, `common/` groups).
- Data access lives in `src/services/` (`api.js`, `liveDataApi.js`, `smartPlannerApi.js`, plus GeoJSON / satellite-map / area helpers). Components do not call `fetch` directly.
- Shared behaviour lives in hooks: `useAuthGate` (role gating), `useAppData` (shared fetches), `useAutoRefresh` (60-second live refresh), `useWorkspace` (workspace context).
- All user-facing strings go through `i18n/translations.js` (`en`, `ml`, `hi`, `ta`) — do not hard-code English copy in a component.
- The app is a plain SPA with no router dependency: `App.jsx` owns navigation and view switching.

## 14c. Data safety rules

- **Never trust client-supplied paths.** Uploads get a generated UUID filename, live under `backend/private_uploads/<user_id>/`, and are validated by magic bytes (JPEG/PNG) and a 5 MB cap.
- **Never leak existence.** A record the caller may not see returns `404`, not `403` (see `apps/smart_planner/routes.py`).
- **Never return another user's record** without an explicit officer/admin role check.
- **Live data is labelled.** Fallback market prices and default-location weather must stay clearly marked as pilot/reference data in the payload and in the UI.
- **Pilot data only.** `backend/core/seed_data.py` and `backend/apps/operations/seed.py` create demo accounts and illustrative rows for the `farmer` account; they must be removed before any real deployment.

## 15. Git & team development

Feature-based branches (`feature/subsidy-module`, `feature/irrigation-module`, …) and descriptive commits ("Add personalized subsidy matching", "Fix missing-document detection") — never "update"/"final".

## 16. Definition of done

A feature is complete only when: code is separated into logical files; business logic and UI are separated; AI is separated from deterministic rules; APIs are separated by feature; errors are handled; important operations are logged; tests exist; documentation exists; no secrets are committed; and another developer can understand the feature without reading unrelated modules.
