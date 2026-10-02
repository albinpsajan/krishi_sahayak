# 🌱 KrishiSahayak AI

AI-assisted, officer-verified agricultural administration platform connecting **Farmers** and **Agricultural Officers** (Kerala, India).

> **Core principle:** AI handles repetitive tasks and explanations. Humans make all important decisions.
> The AI layer never invents subsidy amounts, eligibility rules, deadlines or required documents — those live in officer-managed data and deterministic rules.

- **Backend:** FastAPI + SQLAlchemy + SQLite · **Frontend:** React 18 + Vite (SPA)
- **Languages:** English, മലയാളം (Malayalam), हिन्दी, தமிழ் · **Roles:** `FARMER`, `OFFICER`, `ADMIN`
- **API version:** 1.1.0 · **Docs:** [`docs/architecture.md`](docs/architecture.md), [`docs/api.md`](docs/api.md), [`docs/features/`](docs/features)

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Quickstart](#quickstart)
- [Demo credentials](#demo-credentials)
- [Environment variables](#environment-variables)
- [Project structure](#project-structure)
- [API surface](#api-surface)
- [Data model](#data-model)
- [Security model](#security-model)
- [Running tests](#running-tests)
- [Seeded demo data](#seeded-demo-data)
- [Known limitations](#known-limitations)
- [Contributing](#contributing)

---

## Features

| Feature | What it does |
|---|---|
| **Farmer Digital Profile** | Accounts, two-step onboarding, single source of truth for farm data (district, land size, crops, water source, KCC) |
| **Crop Cases (CropDoctor)** | Photo-based crop disease cases with a *preliminary* AI assessment stored separately from the officer decision |
| **Officer Verification** | Human-in-the-loop: the officer confirms or corrects every AI diagnosis and issues the recommendation |
| **SubsidyChain** | Personalized subsidy matching with deterministic eligibility screening and missing-document detection |
| **AutoClerk** | One-click official administrative report generation from a case |
| **Audit Ledger** | Tamper-evident SHA-256 hash chain of every important action, with a chain-integrity verifier |
| **Notifications** | Bilingual (English / മലയാളം) in-app alerts with read/unread tracking |
| **Smart Planner** | Farmer-drawn GeoJSON plot boundaries, approximate area, coconut spacing, irrigation choices, intercrops and reviewable material estimates |
| **Live field signals** | In-app weather (Open-Meteo), market-price cards, one-minute auto-refresh and multilingual labels |
| **Voice / text assistant** | Browser Web Speech API input with rule-based intent detection, typed-input fallback |
| **Farm operations** | Plots and crop seasons, shared resource catalogue, booking requests, farmer cooperation groups, cashbook and a document checklist |
| **Community board** | Crop-wise discussion boards with officer moderation (moderation ≠ agronomic verification) |
| **Market watch** | Commodity prices by state / district / market with a labelled pilot fallback dataset |

### Smart Planner

The Smart Planner opens a satellite view using browser location or village search. The farmer confirms the real plot by clicking and dragging geographic pins on the imagery, then receives a preliminary coconut layout with configurable 7.5 m spacing, irrigation guidance, intercrop suggestions and a low/high material estimate. Farmers can save a plan, create new versions through the customization panel and send it to an officer; officers can approve it, request changes or ask for a field check.

The feature is deliberately split into inspectable modules:

```
backend/apps/smart_planner/     # models, schemas, rules, services and routes
frontend/src/pages/SmartPlannerPage.jsx
frontend/src/components/smartPlanner/  # satellite picker, SVG plan, version history, result cards
frontend/src/services/smartPlannerApi.js
```

The selected boundary is stored as WGS84 GeoJSON and projected to local metres for spacing calculations. Satellite imagery assists farmer selection; it does not detect, certify or infer legal ownership. Field verification remains necessary before construction or planting.

### Live data & assistant

Weather is fetched through the backend from **Open-Meteo** and cached for 60 seconds (default coordinates: Palakkad, Kerala — 10.7867, 76.6548). Market prices use the modular market service and currently return clearly labelled **pilot fallback data** until a verified state feed is configured. The dashboard keeps the last good response when a refresh fails. English, Malayalam, Hindi and Tamil are stored locally as the selected interface language; voice uses the browser Web Speech API with typed input as a fallback.

---

## Tech stack

### Backend (Python 3.10+)

| Layer | Choice |
|---|---|
| Web framework | FastAPI `>=0.110` |
| ASGI server | Uvicorn `>=0.29` |
| ORM | SQLAlchemy `>=2.0` |
| Database | SQLite (`backend/krishi_sahayak.db`, overridable via `DATABASE_URL`) |
| Validation / schemas | Pydantic `>=2.6` |
| Auth | PyJWT `>=2.8` (HS256, 24 h expiry), PBKDF2-HMAC-SHA256 password hashing (600 000 rounds) |
| Uploads | `python-multipart`, `email-validator` |

Everything else used is Python standard library (`hashlib`, `hmac`, `urllib`, `json`, `secrets`, `math`, …) — no extra runtime dependency.

### Frontend (Node 18+)

| Package | Version |
|---|---|
| `react` / `react-dom` | `^18.2.0` |
| `vite` | `^5.1.6` |
| `@vitejs/plugin-react` | `^4.2.1` |
| `leaflet` | `^1.9.4` (Smart Planner satellite map) |
| `lucide-react` | `^0.344.0` (icons) |

State management is plain React hooks plus a small set of custom hooks (`useAuthGate`, `useAppData`, `useAutoRefresh`, `useWorkspace`) and one context provider (`i18n/languageContext.jsx`). **No router, store or UI-kit dependency** — navigation and view switching are handled inside `App.jsx`.

---

## Quickstart

### 1. Backend

```bash
pip install -r requirements.txt
python run_app.py                 # serves http://127.0.0.1:8000
```

`run_app.py` puts `backend/` on `sys.path` and starts Uvicorn on port `8000` (override with `PORT`). Set `KRISHI_RELOAD=1` for auto-reload during development.

The SQLite database is created, migrated and seeded automatically on first run — no manual migration step. On a fresh checkout `GET /` returns the API banner; once the frontend is built it returns the SPA.

### 2. Frontend (dev, with hot reload)

```bash
cd frontend
npm install
npm run dev                       # serves http://localhost:3000, proxies /api and /assets -> :8000
```

### 3. Single-port mode (production-like)

```bash
cd frontend && npm run build      # emits frontend/dist/ (gitignored)
cd .. && python run_app.py        # FastAPI serves the built SPA on http://127.0.0.1:8000
```

### Production server

```bash
cd frontend && npm run build
uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs` (Swagger UI) and `/redoc`.

---

## Demo credentials

| Role | Login | Password |
|---|---|---|
| 👨‍🌾 Farmer | `farmer` (or `farmer@krishi.in`) | `farmer123` |
| 🏛️ Officer | `officer` (or `officer@krishi.in`) | `officer123` |

These accounts are created by `backend/core/seed_data.py` and are **local demo data only** — change or delete them before any real deployment.

---

## Environment variables

All settings are read from the **process environment** by `backend/config/settings.py`. `.env.example` is a template that documents every supported variable; the application does **not** auto-load a `.env` file, so export the variables in your shell (or use a process manager / container env) before starting the app.

| Variable | Default | Purpose |
|---|---|---|
| `JWT_SECRET_KEY` | insecure dev fallback | Secret used to sign HS256 access tokens. **Must be set in production.** |
| `KRISHI_DB_PATH` | `backend/krishi_sahayak.db` | SQLite file location. Leave empty for the default. |
| `DATABASE_URL` | `sqlite:///<KRISHI_DB_PATH>` | Full SQLAlchemy URL; overrides `KRISHI_DB_PATH` when set. |
| `CROP_DOCTOR_API_KEY` | empty | Optional external vision provider key for CropDoctor AI (demo works without it). |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins. `*` is for local development only. |
| `PORT` | `8000` | Port used by `run_app.py`. |
| `KRISHI_RELOAD` | unset | Set to `1` to enable Uvicorn auto-reload. |

`.env` is gitignored; only `.env.example` with placeholders is committed. The app runs without any of these for local development (fallback JWT secret, local SQLite, local AI knowledge base).

---

## Project structure

```
krishi-sahayak/
├── run_app.py              # Launcher: sys.path + Uvicorn on :8000
├── requirements.txt        # Backend Python dependencies
├── .env.example            # Environment variable template
├── backend/
│   ├── main.py             # Thin FastAPI app factory (routers + static mounts + startup)
│   ├── config/settings.py  # Every tunable value, environment-driven
│   ├── core/               # database, security, errors, logging_config, seed_data
│   ├── api/                # One router file per feature
│   │   ├── auth_routes.py        # /api/auth
│   │   ├── profile_routes.py      # /api/profile
│   │   ├── upload_routes.py       # /api/upload, /api/uploads/{owner_id}/{filename}
│   │   ├── case_routes.py         # /api/cases
│   │   ├── subsidy_routes.py      # /api/subsidies
│   │   ├── officer_routes.py      # /api/officer
│   │   ├── audit_routes.py        # /api/audit
│   │   ├── notification_routes.py # /api/notifications
│   │   ├── operation_routes.py    # /api/operations
│   │   ├── community_routes.py    # /api/community
│   │   ├── live_data_routes.py    # /api/weather, /api/market-prices, /api/assistant
│   │   └── __init__.py            # Router registry
│   ├── apps/               # Feature packages (models, schemas, services)
│   │   ├── farmer_profile/ # User, FarmerProfile, OfficerProfile + profile_service
│   │   ├── crop_cases/     # CropCase, CropImage, AIAssessment, OfficerReview, Recommendation
│   │   ├── subsidies/      # Schemes, applications + matcher / eligibility / document checkers
│   │   ├── audit/          # Hash-chained audit ledger
│   │   ├── notifications/  # Notification service
│   │   ├── autoclerk/      # Official report generator
│   │   ├── operations/     # Plots, resources, bookings, cooperation groups, cashbook, documents
│   │   ├── community/      # Moderated crop-board posts
│   │   ├── smart_planner/  # Plots, plans, reviews, versions + geometry/layout rules
│   │   └── farms/          # Farm / irrigation models (engine not implemented yet)
│   ├── ai/                 # crop_doctor.py + knowledge_base.py (explains only; never decides)
│   ├── services/           # weather, market price, assistant intent, plan customization, cache
│   └── private_uploads/    # Gitignored, created at startup
├── frontend/
│   ├── index.html
│   ├── vite.config.js      # React plugin, base './', dev :3000, proxies /api + /assets
│   ├── package.json
│   └── src/
│       ├── App.jsx          # Shell, navigation and view switching (no router dependency)
│       ├── main.jsx         # React entrypoint
│       ├── LegacyApp.jsx    # Pre-split single-file app kept for reference
│       ├── pages/           # 20 screens (FarmerDashboard, OfficerDashboard, SmartPlannerPage, …)
│       ├── components/     # Modals, ui primitives, market / weather / voice / smartPlanner groups
│       ├── layouts/        # Header, NavBar, WorkspaceLayout
│       ├── hooks/          # useAuthGate, useAppData, useAutoRefresh, useWorkspace
│       ├── services/       # api.js, liveDataApi, smartPlannerApi, geoJson / satellite / area helpers
│       ├── i18n/           # languageContext.jsx + translations.js (en / ml / hi / ta)
│       ├── utils/          # format.js, roles.js
│       └── *.css           # theme, liveData, smartPlanner, journal, readability, responsive
├── tests/                  # unittest suites mirroring the features
│   ├── test_environment.py # Shared bootstrap + isolated temp database
│   ├── test_live_data.py
│   ├── test_workflows.py
│   ├── ai/  audit/  autoclerk/  farmer_profile/  smart_planner/  subsidies/
├── docs/                   # architecture.md, api.md, features/<feature>.md
├── assets/                 # Uploads served at /uploads (gitignored except sample_leaf.jpg)
└── scripts/                # Reserved for developer helper scripts
```

---

## API surface

Base URL `http://127.0.0.1:8000` · Auth header `Authorization: Bearer <token>` · Full reference in [`docs/api.md`](docs/api.md).

| Prefix | Router | Feature |
|---|---|---|
| `/api/auth` | `api/auth_routes.py` | register, login, onboarding details, current user |
| `/api/profile` | `api/profile_routes.py` | role-aware profile (farmer farm facts or officer record) |
| `/api/upload`, `/api/uploads/…` | `api/upload_routes.py` | private crop photo upload and authenticated retrieval |
| `/api/cases` | `api/case_routes.py` | crop cases, AI assessment, officer review, status transitions |
| `/api/subsidies` | `api/subsidy_routes.py` | scheme directory, apply, applications, officer decision |
| `/api/officer` | `api/officer_routes.py` | AutoClerk official report for a case |
| `/api/audit` | `api/audit_routes.py` | ledger timeline and chain-integrity verification |
| `/api/notifications` | `api/notification_routes.py` | own notifications, mark one as read |
| `/api/operations` | `api/operation_routes.py` | plots, resources, bookings, cooperation groups, cashbook, document checklist |
| `/api/community` | `api/community_routes.py` | crop-board posts and officer moderation |
| `/api/smart-planner` | `apps/smart_planner/routes.py` | rules, plots, plans, reviews, versions, farm locations |
| `/api/weather`, `/api/market-prices`, `/api/assistant` | `api/live_data_routes.py` | live signals and voice/text assistant |

Every error response raised through `core/errors.py` uses the same envelope:

```json
{ "detail": { "code": "SCHEME_NOT_FOUND", "message": "Subsidy scheme not found" } }
```

---

## Data model

SQLAlchemy models, grouped by owning feature package:

| Feature | Models |
|---|---|
| `farmer_profile` | `User`, `FarmerProfile`, `OfficerProfile` |
| `crop_cases` | `CropCase`, `CropImage`, `AIAssessment`, `OfficerReview`, `Recommendation` |
| `subsidies` | `SubsidyScheme`, `SubsidyApplication`, `ApplicationDocument` |
| `audit` | `AuditRecord` (with `previous_hash` / `current_hash` chain) |
| `notifications` | `Notification` |
| `operations` | `Resource`, `Booking`, `Cooperation`, `Participant`, `CashEntry`, `DocumentCheck`, `Activity` |
| `community` | `CommunityPost` |
| `smart_planner` | `SmartPlot`, `SmartPlan`, `SmartPlanReview`, `FarmLocation`, `PlanVersion`, `PlanChangeRequest` |
| `farms` | `Farm`, `FarmCrop` (live, used by farm operations) + `IrrigationPlan`, `IrrigationComponent`, `IrrigationOfficerReview` (placeholders) |

Tables are created with `Base.metadata.create_all()` on startup, followed by `run_lightweight_migrations()` which adds missing columns and indexes to existing databases (for example `users.username`, `users.age`, `users.profile_completed` and a unique index on `username`).

---

## Security model

- **Passwords** are stored as `pbkdf2_sha256$600000$<salt>$<digest>`; verification is constant-time.
- **Tokens** are HS256 JWTs valid for 24 hours, signed with `JWT_SECRET_KEY`.
- **Roles** `FARMER` / `OFFICER` / `ADMIN` are enforced by the `get_current_user()`, `require_farmer()` and `require_officer()` dependencies in `core/security.py`.
- **Ownership** is checked on every case, application, plot and plan read — farmers see only their own records; officers and admins see all.
- **Photo privacy** — crop images are stored under `backend/private_uploads/<user_id>/` with a random filename, are served only to the owner or an officer/admin, and are capped at 5 MB with JPEG/PNG magic-byte validation.
- **Audit** — every meaningful mutation is appended to the hash-chained ledger; `GET /api/audit/verify` re-walks the chain and reports `VALID` or `TAMPERED`.
- **No secrets in code.** Only placeholders live in `.env.example`; the JWT fallback in `config/settings.py` exists for local demos only and must be overridden in production.

---

## Running tests

```bash
python -m unittest discover -s tests -t . -v
```

`tests/test_environment.py` points `KRISHI_DB_PATH` at a per-process temporary file **before** any backend module is imported, so the suite never touches the developer's real database.

Coverage: subsidy matching, eligibility rules, document checking, audit-ledger tamper evidence, CropDoctor output contract, auth security (wrong-secret token, hashing), profile workflows, Smart Planner geometry/layout rules, live-data endpoints and end-to-end workflows.

---

## Seeded demo data

`backend/core/seed_data.py` and `backend/apps/operations/seed.py` run on startup and are safe to re-run (each exits early if its demo rows already exist). They create:

1. **Farmer** — Ramanan Nair, Palakkad (Kerala), 46, 3.5 acres, "Paddy (Uma), Pepper, Coconut", Malampuzha Canal & Borewell, KCC holder, language `ml`.
2. **Officer** — Dr. Lakshmi Priya, code `KL-AGRI-409`, Senior Agricultural Officer & Krishi Bhavan Chief, Palakkad District.
3. **Three subsidy schemes** — `SCH-PADDY-01` (₹15,000 max), `SCH-SPICE-02` (₹8,000 max), `SCH-SOLAR-03` (₹85,000 max) with Malayalam names, eligibility criteria, required documents and benefits.
4. **One verified sample crop case** — `CASE-2026-8801` (Paddy, Uma MO-16, Chittur East) with a crop image, a preliminary CropDoctor assessment (Paddy Blast, 89.5 % confidence), a confirmed officer review with Malayalam recommendation, a product recommendation, three audit entries and one notification.
5. **Farm-operations demo data** — four shared resources (tractor, transport, pump, harvesting team), three plots with crop seasons, one cooperation group and four cashbook entries.

To start from a clean database, stop the server and delete `backend/krishi_sahayak.db`.

---

## Known limitations

- **Market prices are pilot fallback data**, clearly labelled as such, until a verified state feed is configured. The service is modular so a real provider can be dropped in.
- **CropDoctor runs on a local knowledge base.** An external vision provider can be enabled with `CROP_DOCTOR_API_KEY`, but no diagnosis is auto-authoritative — every assessment stays *preliminary* until an officer reviews it.
- **Irrigation planning is not implemented.** `apps/farms/` holds the `Irrigation*` models as placeholders; the plan engine and its router are future work (see [`docs/features/irrigation.md`](docs/features/irrigation.md)).
- **SQLite only.** Fine for the pilot; point `DATABASE_URL` at PostgreSQL for multi-user deployment.
- **No refresh tokens** — sessions end when the 24-hour token expires.
- **Satellite imagery assists selection only** and never certifies land ownership or boundaries.
- **Served over plain HTTP locally.** Deploy behind TLS and set `CORS_ORIGINS` explicitly for anything beyond the demo.
- **No push/email delivery** — notifications are in-app only.

---

## Contributing

Read [`docs/architecture.md`](docs/architecture.md) first — it defines the project's non-negotiable rules (feature-based separation, AI never owns business rules, one responsibility per file, single source of truth, change isolation). Before calling a feature done, confirm it satisfies the *definition of done* in section 16 of that document, and add or update `docs/features/<feature>.md`.

Use descriptive feature branches (`feature/subsidy-module`, `feature/irrigation-module`, …) and meaningful commit messages ("Add personalized subsidy matching", "Fix missing-document detection") — never "update" or "final".
