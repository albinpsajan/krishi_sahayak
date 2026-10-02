# 🌱 KrishiSahayak 

AI-Assisted, Officer-Verified Agricultural Administration Platform connecting **Farmers** and **Agricultural Officers** (Kerala, India).

> **Core principle:** AI handles repetitive tasks and explanations. Humans make all important decisions.
> The AI layer never invents subsidy amounts, eligibility rules, deadlines or required documents — those live in officer-managed data and deterministic rules.

## Features

| Feature | What it does |
|---|---|
| **Farmer Digital Profile** | Accounts, onboarding, single source of truth for farm data |
| **Crop Cases (CropDoctor)** | Photo-based crop disease cases with preliminary AI assessment |
| **Officer Verification** | Human-in-the-loop: officer confirms or corrects every AI diagnosis |
| **SubsidyChain** | Personalized subsidy matching with deterministic eligibility screening |
| **AutoClerk** | One-click official administrative report generation |
| **Audit Ledger** | Tamper-evident SHA-256 hash chain of every important action |
| **Notifications** | Bilingual (English / മലയാളം) in-app alerts |
| **Smart Planner** | Farmer-drawn plot boundaries, approximate area, coconut spacing, irrigation choices, intercrops and reviewable material estimates |
| **Live field signals** | In-app weather, market-price cards, one-minute refresh, multilingual labels and voice/text assistant |

### Smart Planner

The Smart Planner opens a satellite view using browser location or village search. The farmer confirms the real plot by clicking and dragging geographic pins on the imagery, then receives a preliminary coconut layout with configurable 7.5 m spacing, irrigation guidance, intercrop suggestions and a low/high material estimate. Farmers can save a plan and send it to an officer; officers can approve it, request changes or ask for a field check.

The feature is deliberately split into inspectable modules:

```
backend/apps/smart_planner/  # models, schemas, rules, services and routes
frontend/src/pages/SmartPlannerPage.jsx
frontend/src/components/smartPlanner/  # satellite picker, SVG plan and result cards
frontend/src/services/smartPlannerApi.js
```

The selected boundary is stored as WGS84 GeoJSON and projected to local metres for spacing calculations. Satellite imagery assists farmer selection; it does not detect, certify or infer legal ownership. Field verification remains necessary before construction or planting.

Weather is fetched through the backend from Open-Meteo and cached for 60 seconds. Market prices use the modular market service and currently return clearly labelled pilot fallback data until a verified state feed is configured. The dashboard keeps the last response when a refresh fails. English, Malayalam, Hindi and Tamil are stored locally as the selected interface language; voice uses the browser Web Speech API with typed input as a fallback.

## Quickstart

```bash
# 1. Backend (Python 3.10+, see requirements.txt)
pip install -r requirements.txt
python run_app.py                 # serves http://127.0.0.1:8000

# 2. Frontend (Node 18+)
cd frontend
npm install
npm run dev                       # serves http://localhost:3000 (proxies /api -> :8000)
```

The SQLite database (`backend/krishi_sahayak.db`) is created and seeded automatically on first run.

**Demo credentials**

| Role | Login | Password |
|---|---|---|
| 👨‍🌾 Farmer | `farmer` (or farmer@krishi.in) | `farmer123` |
| 🏛️ Officer | `officer` (or officer@krishi.in) | `officer123` |

## Environment variables

Copy `.env.example` to `.env` and fill in real values. **Never commit `.env`** (it is gitignored).
The app works without a `.env` for local development (fallback JWT secret, local SQLite, local AI knowledge base).

## Running tests

```bash
python -m unittest discover -s tests -t . -v
```

The test suite covers subsidy matching, eligibility rules, document checking, audit ledger tamper-evidence, AI output contracts, auth security, profile workflows and Smart Planner geometry/layout rules.

## Project structure

```
krishi-sahayak/
├── backend/
│   ├── main.py              # Thin FastAPI app factory
│   ├── api/                 # One router file per feature (auth, cases, subsidies, ...)
│   ├── apps/                # Feature packages (models, schemas, services)
│   │   ├── farmer_profile/  # Users, profiles + profile_service (single source of truth)
│   │   ├── crop_cases/      # CropCase, AIAssessment, OfficerReview
│   │   ├── subsidies/       # Schemes + deterministic matcher/eligibility/document checkers
│   │   ├── audit/           # Hash-chained audit ledger
│   │   ├── notifications/   # Notification service
│   │   ├── autoclerk/       # Official report generator
│   │   └── farms/           # Farm/irrigation models (future feature)
│   ├── ai/                  # AI layer (explains only; never decides)
│   ├── core/                # Database, security, errors, logging, seed data
│   └── config/              # Environment-driven settings
├── frontend/src/
│   ├── pages/               # One file per screen
│   ├── components/          # Reusable modals
│   ├── layouts/             # Header, NavBar
│   ├── hooks/               # useAuthGate, useAppData
│   ├── services/            # API client
│   └── utils/               # Role helpers
├── tests/                   # Per-feature test packages
└── docs/                    # Architecture, API reference, feature docs
```

See **[docs/architecture.md](docs/architecture.md)** for the design rules and **[docs/api.md](docs/api.md)** for the endpoint reference.
