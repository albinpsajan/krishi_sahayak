# KrishiSahayak AI — API Reference

Base URL: `http://127.0.0.1:8000` · Interactive docs: `/docs` (Swagger UI)

Authentication: `Authorization: Bearer <token>` from `POST /api/auth/login` or `POST /api/auth/register`.
Errors return `{ "detail": { "code": "<MACHINE_CODE>", "message": "<human message>" } }`.

## Auth — `/api/auth` (farmer_profile feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Step 1 signup (email, username, password). Returns JWT. |
| POST | `/api/auth/login` | — | Login with email **or** username + password. Returns JWT. |
| PUT | `/api/auth/details` | ✓ | Step 2 onboarding: full name, age, role (FARMER/OFFICER), phone. |
| GET | `/api/auth/me` | ✓ | Current user object. |

## Profile — `/api/profile` (farmer_profile feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/profile` | ✓ | Account facts + role-specific profile (farm or officer). |

## Uploads — `/api/upload`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/upload` | ✓ | Multipart image upload; returns `{file_url}` served from `/uploads/`. |

## Crop Cases — `/api/cases` (crop_cases feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/cases` | ✓ | Farmers: own cases. Officers: all cases. |
| POST | `/api/cases` | Farmer | Create case; triggers preliminary CropDoctor AI assessment. |
| GET | `/api/cases/{case_id}` | ✓ | Full case record (images, AI assessment, officer review). |
| POST | `/api/cases/{case_id}/review` | Officer | Officer verification: confirm/correct diagnosis, issue recommendation. |

## Subsidies — `/api/subsidies` (subsidies feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/subsidies` | — | Officer-managed scheme directory. |
| POST | `/api/subsidies/apply` | Farmer | Submit application; deterministic SubsidyChain screening assigns `risk_level`. |
| GET | `/api/subsidies/applications` | ✓ | Farmers: own applications. Officers: all. |
| POST | `/api/subsidies/applications/{id}/decide` | Officer | Approve / Reject / Info Requested (sole officer authority). |

Risk levels from the rule engine: `LOW_RISK_FAST_TRACK`, `HUMAN_REVIEW_REQUIRED`, `INCOMPLETE_DOCUMENTS`. The engine never auto-approves or auto-rejects.

## Officer — `/api/officer` (autoclerk feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/officer/autoclerk/{case_id}` | Officer | Generated official administrative report (markdown). |

## Audit — `/api/audit` (audit feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/audit/ledger` | ✓ | Full hash-chained audit timeline. |
| GET | `/api/audit/verify` | — | Re-walks the SHA-256 chain; returns `VALID` or `TAMPERED` + corrupted id. |

## Notifications — `/api/notifications` (notifications feature)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications` | ✓ | Own notifications (English + Malayalam). |
| PUT | `/api/notifications/{id}/read` | ✓ | Mark one as read. |

## Future: irrigation — `/api/farms` (planned)

`apps/farms/` models exist (Farm, FarmCrop, IrrigationPlan, components, officer reviews); the plan engine and its router are the next feature branch.
