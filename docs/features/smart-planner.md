# Smart Planner

## Purpose
Let a farmer confirm their real plot on satellite imagery, get an explainable preliminary coconut + irrigation layout with a material estimate, iterate on it through versions, and then hand it to an officer for a decision.

> **Boundary honesty rule.** The satellite picker *helps a farmer select a plot*. It does not detect, certify or infer legal ownership. Every generated plan carries a disclaimer and a `next_action` telling the farmer to request officer review before buying anything. The officer's decision is the only authority in the loop.

## Inputs
- **Boundary** — either a WGS84 GeoJSON `Polygon` (from the satellite picker, browser geolocation or village search) or a plain local-metre point list.
- **Plan preferences** (`PlanCreate`) — main crop, water source (`well`/`borewell`/`pond`/`canal`/`rainfed`/`other`/`not sure`), soil type, budget level, irrigation preference, plantation type, coconut age (`new`/`1–3 years`/`4–7 years`/`mature`), notes.
- **Change request** (`ChangeRequest`) — change type and note, applied as a new plan version.

## Outputs
- **Plot analysis** — area in m², acres, cents and hectares; perimeter; `shape_type`; `usable_area_sq_m` (93 % of gross); plus, for GeoJSON input, the normalised polygon and its centroid.
- **Coconut layout** — 7.5 m × 7.5 m square spacing with a 2 m boundary buffer, tree positions, row count, plants-per-row estimate and a `rule_note` telling the farmer to verify locally.
- **Irrigation plan** — recommended method with its reason, main/sub-main/lateral pipe lengths, dripper and sprinkler counts, filter and valve requirement, and a line layout.
- **Intercrop options** — two possibilities for the given coconut age, each labelled `Possible option` with water and labour requirements and a season note.
- **Material estimate** — line items with a low/high cost range per unit and a total range, all marked `Rough planning range`.
- **`layout_svg`** — a self-contained SVG of the boundary, trees, pipes, drippers, sprinkler coverage and the intercrop zone.
- **`disclaimer` + `next_action`** on every plan.

## Main files
| File | Responsibility |
|---|---|
| `apps/smart_planner/rules.py` | Editable agronomy and cost reference tables (defaults, not quotes) |
| `apps/smart_planner/services.py` | Pure calculations — no database, no HTTP: `validate_boundary`, `polygon_area`, `geojson_to_local`, `analyse_plot`, `analyse_geojson`, `coconut_layout`, `irrigation_plan`, `intercrops`, `material_estimate`, `render_layout_svg`, `generate_plan` |
| `apps/smart_planner/models.py` | `SmartPlot`, `SmartPlan`, `SmartPlanReview`, `FarmLocation`, `PlanVersion`, `PlanChangeRequest` |
| `apps/smart_planner/schemas.py` | `PlotCreate`, `PlanCreate`, `ReviewCreate`, `ReviewUpdate`, `LocationCreate`, `ChangeRequest` |
| `apps/smart_planner/routes.py` | HTTP boundary, role guards, ownership checks, notifications |
| `services/plan_customization_service.py` | `apply_change()` — turns a change request into a new layout |
| `frontend/src/pages/SmartPlannerPage.jsx` | The screen |
| `frontend/src/components/smartPlanner/SatellitePlotMap.jsx` | Leaflet map + draggable pins |
| `frontend/src/components/smartPlanner/PlanVisual.jsx` | Renders `layout_svg` |
| `frontend/src/components/smartPlanner/PlanCustomizationPanel.jsx` | Change requests |
| `frontend/src/components/smartPlanner/PlanVersionHistory.jsx` | Version timeline |
| `frontend/src/components/smartPlanner/PlanCards.jsx`, `PlannerLiveSignals.jsx` | Result cards and live weather/price context |
| `frontend/src/services/smartPlannerApi.js`, `geoJsonService.js`, `satelliteMapService.js`, `areaCalculationService.js`, `plotLocationService.js` | Client-side API and geometry helpers |

## Database models
`SmartPlot` (farmer, plot name, village, district, `boundary_json` holding either the local boundary or a `{local_boundary, geojson, center_lat, center_lon}` bundle, areas, shape type) · `SmartPlan` (farmer, plot, preferences, status, `plan_json`) · `SmartPlanReview` (one per plan — UNIQUE, officer, status, note, reviewed_at) · `FarmLocation` (latitude, longitude, accuracy, source) · `PlanVersion` (plan, version number, change type, change note, `layout_data`, created_by) · `PlanChangeRequest` (plan, farmer, change type, change note, status).

## API endpoints
`GET /api/smart-planner/rules` (public) · `POST|GET /api/smart-planner/plots` · `GET /api/smart-planner/plots/{id}` · `POST /api/smart-planner/plans/generate` · `GET /api/smart-planner/plans` · `GET /api/smart-planner/plans/{id}` · `POST /api/smart-planner/plans/{id}/request-review` · `GET /api/smart-planner/officer/pending` · `PATCH /api/smart-planner/plans/{id}/review` · `POST /api/smart-planner/locations` · `GET /api/smart-planner/plans/{id}/versions` · `POST /api/smart-planner/plans/{id}/customize`.

## Deterministic rules (nothing here is a model)
- **Projection** — a WGS84 polygon is projected to local metres about its centroid (`111320 m` per degree of latitude, scaled by `cos(lat0)` for longitude). Good enough for a single small plot; not a survey.
- **Validation** — 3–100 points, finite coordinates within ±100 000, and a minimum polygon area of 25 m².
- **Shape classification** — aspect ratio > 3.0 → `Long and narrow`; 3 points → `Triangular / wedge-like`; sides within 18 % → `Square-like`; ratio < 1.8 → `Rectangular`; otherwise `Irregular`.
- **Coconut layout** — a 7.5 m grid inset by a 2 m buffer, keeping only points inside the polygon (ray-casting), capped at 1000 candidates. The usable-area argument is accepted for interface symmetry with the future engine.
- **Irrigation choice** — an explicit `sprinkler` request wins; otherwise `rainfed`/`other`/`not sure` → *Water source verification required*; low budget or a low-cost preference → *Phased basin → drip*; else → *Drip irrigation*.
- **Pipe sizing** — main `max(0.7 × √usable_area, 18) m`, sub-main `max(rows × 7.5, 12) m`, lateral `trees × 3.1 m`, two drippers per tree for drip, one sprinkler per 16 trees for sprinkler, one valve per 4 rows.
- **Intercrops** — a fixed table keyed on coconut age, with anything unrecognised falling back to `new`.
- **Costs** — a fixed low/high band per material unit; no vendor, region or date is considered.

## AI components
None. The plan is entirely rule-based and inspectable, which is the point: the officer must be able to check the arithmetic.

## Dependencies
`farmer_profile` (auth, farmer id), `notifications` (`create_notification` on review request and on review decision), `core` (db, security). `services/plan_customization_service.py` sits outside the feature because it is shared logic, not a rule table.

## Known limitations
- **Not a survey.** The flat-earth projection is acceptable for a small plot and inaccurate for long or steep sites; slope is not considered at all.
- **The satellite layer assists selection only** — it does not resolve cadastral boundaries.
- **Estimates are planning ranges**, not quotes: no vendor pricing, no transport, no terrain, no labour seasonality, no soil-test data.
- **`irrigation_plan` ignores the `usable_area` argument** for pipe sizing (it uses `plot["usable_area_sq_m"]` directly) and the `budget` argument only affects method selection, not the estimate.
- `render_layout_svg` uses hard-coded SVG dimensions and a fixed scale factor, so very large plots render small and very small plots render coarse.
- Grid layout is square-system only; hexagonal or triangular systems are not offered even though the rules table has a `recommended_system` key.
- **Versioning is append-only and automatic** — the first customization stores the original as version 1, and any version above 1 pushes the plan back to `Sent for Review` without asking.
- The officer can set any status string; there is no review state machine like the booking flow has.
- **No audit entries** are written for plot or plan changes — only notifications.
- `boundary_json` is stored as text with two possible shapes (a bare list or a bundle dict), so readers must branch on the type.

## How to test
`tests/smart_planner/test_services.py` covers the pure calculations. Assert on: projection and area conversion factors, boundary validation rejections, every `shape_type` branch, tree spacing and the boundary buffer, each irrigation-selection branch, pipe/dripper/sprinkler counts, intercrop fallback, cost band totals, and that `generate_plan` always returns `disclaimer` and `next_action`. Route-level ownership, review transitions and version numbering need their own `TestCase` coverage against the isolated test database.
