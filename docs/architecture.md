# KrishiSahayak AI — Architecture & Maintainability

> **Core Development Principle:** a new developer can enter the project, identify a feature, trace its data flow, locate the responsible file, reproduce the bug, and fix it without needing to understand the entire codebase.

## 1. Feature-based separation

Each major functionality lives in its own package. Nothing is a single large file.

- Backend features: `backend/apps/<feature>/` — models, schemas, services per feature.
- Backend API: `backend/api/<feature>_routes.py` — one router per feature.
- Frontend: `pages/`, `components/`, `layouts/`, `hooks/`, `services/`, `utils/`.

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

```
/api/auth/           /api/cases/          /api/subsidies/
/api/officer/        /api/audit/          /api/notifications/
/api/profile         /api/upload
```

Each prefix is served by exactly one router file in `backend/api/`.

## 7. Environment & secrets

All secrets come from environment variables via `backend/config/settings.py` (see `.env.example`). `.env` is gitignored; only `.env.example` with placeholders is committed. No API key, password or secret is hard-coded.

## 8. Error handling

All feature errors go through `core/errors.py::api_error(status, code, message)` producing:

```json
{ "detail": { "code": "SCHEME_NOT_FOUND", "message": "Subsidy scheme not found" } }
```

Codes: `MISSING_FARM_PROFILE`, `SCHEME_NOT_FOUND`, `DOCUMENT_REQUIRED`, `INVALID_APPLICATION_DATA`, `SUBSIDY_MATCHING_ERROR`, `AI_SERVICE_UNAVAILABLE`, `CASE_NOT_FOUND`, `ACCESS_DENIED`, … The user sees the simple message; developers get the code and logs.

## 9. Logging

`core/logging_config.py` provides feature-tagged log lines:

```
[SUBSIDY_MATCH] score=100 risk=LOW_RISK_FAST_TRACK rules_passed=3 flags=0 missing_docs=0
[CROP_CASE] created case_number=CASE-2026-1234 farmer_id=1 crop=Paddy
[SUBSIDY_DECISION] application=SUB-2026-56789 officer_id=2 decision=Approved
```

Logs contain identifiers only — never phone numbers, addresses, document contents or tokens.

## 10. Testing

`tests/` mirrors the features: `subsidies/` (matching, eligibility, documents), `farmer_profile/` (security, profile service), `audit/` (tamper detection), `ai/` (output contract), `autoclerk/`. Covered cases include: eligible farmer, ineligible farmer, missing documents, large landholding, unverified case, tampered ledger, unknown crop, wrong-secret token.

Run: `python -m unittest discover -s tests -t . -v`

Tests use an isolated temp database (`KRISHI_DB_PATH` is redirected by `tests/test_environment.py`), never the developer's real data.

## 11. Documentation

Every feature has `docs/features/<feature>.md` with: purpose, inputs, outputs, main files, database models, API endpoints, AI components, dependencies, known limitations, how to test.

## 12. Naming

Files and functions are descriptive: `subsidy_matcher.py`, `eligibility_checker.py`, `document_checker.py`, `notification_service.py`; `match_farmer_with_subsidies()`, `evaluate_subsidy_application()`, `find_missing_documents()`, `verify_ledger_integrity()`.

## 13. No unnecessary duplication

Cross-feature reads go through services (`profile_service`, `notification_service`) instead of copying rows or logic. One source of truth → multiple features.

## 14. Change isolation

Changing subsidy eligibility touches `apps/subsidies/` only. Irrigation, documents and profile code are untouched. The farms/irrigation feature is a separate package that can grow without affecting live features.

## 15. Git & team development

Feature-based branches (`feature/subsidy-module`, `feature/irrigation-module`, …) and descriptive commits ("Add personalized subsidy matching", "Fix missing-document detection") — never "update"/"final".

## 16. Definition of done

A feature is complete only when: code is separated into logical files; business logic and UI are separated; AI is separated from deterministic rules; APIs are separated by feature; errors are handled; important operations are logged; tests exist; documentation exists; no secrets are committed; and another developer can understand the feature without reading unrelated modules.
