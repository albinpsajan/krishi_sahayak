# Smart Irrigation Advisor (farms) — foundation

## Purpose
Consent-based digital field records backing the upcoming irrigation plan engine and its officer review workflow. **Models are registered and tables exist; the plan engine is intentionally not implemented yet** (change isolation — this feature grows without touching subsidies, cases or profile code).

## Inputs (planned)
Farm boundary polygon + centroid (with explicit `location_permission`), soil type, water source/availability, pump/tank/electricity, crop + growth stage.

## Outputs (planned)
IrrigationPlan: method, confidence (never 100), water requirement, schedule (weather-adjusted), layout, bill of quantities, officer review status flow `DRAFT → AI_GENERATED → SUBMITTED_FOR_REVIEW → UNDER_REVIEW → APPROVED | CHANGES_REQUESTED | REJECTED`.

## Main files
| File | Responsibility |
|---|---|
| `apps/farms/models.py` | Farm, FarmCrop, IrrigationPlan, IrrigationComponent, IrrigationOfficerReview |

## Database models
As above (tables created via `apps/__init__.py` registration).

## API endpoints
None yet — planned under `/api/farms` and `/api/irrigation`.

## AI components
Planned: reasoning + Malayalam explanation fields exist on IrrigationPlan; deterministic engine decides parameters, AI explains them (same rule as subsidies).

## Dependencies
farmer_profile (Farm.farmer), core.

## Known limitations
- Engine, weather integration, cost tables and review endpoints are future branches.

## How to test
Model-level tests will live in `tests/irrigation/` once the engine lands.
