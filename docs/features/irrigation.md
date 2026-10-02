# Smart Irrigation Advisor (farms) — foundation

## Purpose
Consent-based digital field records backing the upcoming irrigation plan engine and its officer review workflow. **The plan engine is intentionally not implemented yet** (change isolation — this feature grows without touching subsidies, cases or profile code).

> **Status note:** `Farm` and `FarmCrop` from this package are *already in production use* by the farm-operations feature, which creates plots and crop seasons through `/api/operations/plots`. Only the `Irrigation*` models below are unused placeholders.

## Inputs (planned)
Farm boundary polygon + centroid (with explicit `location_permission`), soil type, water source/availability, pump/tank/electricity, crop + growth stage.

## Outputs (planned)
IrrigationPlan: method, confidence (never 100), water requirement, schedule (weather-adjusted), layout, bill of quantities, officer review status flow `DRAFT → AI_GENERATED → SUBMITTED_FOR_REVIEW → UNDER_REVIEW → APPROVED | CHANGES_REQUESTED | REJECTED`.

## Main files
| File | Responsibility |
|---|---|
| `apps/farms/models.py` | `Farm`, `FarmCrop` (live) + `IrrigationPlan`, `IrrigationComponent`, `IrrigationOfficerReview` (planned) |

## Database models
`Farm` and `FarmCrop` are written by `api/operation_routes.py` today. The three `Irrigation*` models have their tables created via `apps/__init__.py` registration but are never read or written.

## API endpoints
None for irrigation. The plot endpoints that touch `Farm`/`FarmCrop` are `GET|POST /api/operations/plots` — see [`operations.md`](operations.md).

## AI components
Planned: reasoning + Malayalam explanation fields exist on `IrrigationPlan`; a deterministic engine would decide the parameters and AI would explain them (same rule as subsidies). **No irrigation AI exists today** — do not describe it as working in any user-facing text.

## Dependencies
farmer_profile (Farm.farmer), core, and (already today) `apps/operations`.

## Known limitations
- Engine, weather integration, cost tables and review endpoints are future branches.
- There is no plan-status state machine yet, so nothing enforces `DRAFT → … → APPROVED`.

## How to test
Model-level tests will live in `tests/irrigation/` once the engine lands. `Farm`/`FarmCrop` behaviour is currently only covered indirectly by `tests/test_workflows.py`.
