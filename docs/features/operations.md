# Farm Operations

## Purpose
The daily working layer of the platform: what a farmer actually books, joins, spends and earns. It is deliberately a set of small, independent records rather than one large "operations" blob, so a change to booking logic never touches the cashbook.

## Inputs (validated Pydantic contracts in `apps/operations/schemas.py`)
- **Plot** — name, crop, variety, area (acres), water source, planting date, growth stage (`initial`/`vegetative`/`flowering`/`fruiting`/`maturity`).
- **Booking** — resource, date, slot (`Morning`/`Afternoon`), notes, client-generated `request_key`.
- **Cooperation group** — title, category (`Group selling`/`Shared machinery`/`Group buying`/`Transport`), location, date, description.
- **Cash entry** — crop, category, kind (`Income`/`Expense`), amount, date, note.
- **Profile update** — full name, phone, district, water source.
- **Document tick** — one of `Identity proof`, `Land record`, `Bank details`, `Crop insurance`, `Application receipt`.

## Outputs
- Plot lists enriched with the most recent crop record (crop name, planting date, growth stage) or `Not planted`.
- Booking views enriched with resource name and provider, plus a validated status flow.
- Group views enriched with member count, whether the caller has joined, and the full activity history.
- Cashbook entries newest first, and the ticked-off document names.

## Main files
| File | Responsibility |
|---|---|
| `apps/operations/models.py` | Relational records only — no request logic |
| `apps/operations/schemas.py` | Input contracts and the literal value sets |
| `apps/operations/service.py` | Workflow rules: `record()`, `transition_booking()`, `booking_view()` |
| `apps/operations/seed.py` | Illustrative demo data attached only to the seeded `farmer` account |
| `api/operation_routes.py` | HTTP boundary, role guards, audit calls |
| `apps/farms/models.py` | `Farm` and `FarmCrop` — the shared plot/crop-season models this feature writes |
| `frontend/src/pages/FarmPage.jsx` | Plots, resources, bookings |
| `frontend/src/pages/TogetherPage.jsx` | Cooperation groups |
| `frontend/src/pages/CashbookPage.jsx` | Income/expense ledger |
| `frontend/src/pages/ResourcesPage.jsx` | Shared resource catalogue |

## Database models
`Resource` (name, category, provider, location, rate, unit, description) · `Booking` (farmer, resource, date, slot, notes, status, `request_key` unique, `reservation_key` unique set only on confirmation) · `Cooperation` (title, category, location, date, description, status, owner) · `Participant` (unique per case+farmer) · `CashEntry` (farmer, crop, category, kind, amount, date, note) · `DocumentCheck` (unique per farmer+name) · `Activity` (actor, target type/id, message, timestamp) — the per-group history.

## API endpoints
`GET|POST /api/operations/plots` · `PUT /api/operations/profile` · `GET /api/operations/resources` · `GET|POST /api/operations/bookings` · `PATCH /api/operations/bookings/{id}` · `GET|POST /api/operations/groups` · `POST /api/operations/groups/{id}/join` · `PATCH /api/operations/groups/{id}` (officer) · `GET|POST /api/operations/cashbook` · `GET /api/operations/documents` · `PUT /api/operations/documents/{name}`.

## Workflow rules (all in `service.py`, not the router)
- **Booking status** — `Requested → Confirmed | Cancelled`, `Confirmed → Completed | Cancelled`. Any other move is `409`.
- **Authority** — a farmer may only cancel their own request. Confirming and completing are coordinator (officer/admin) actions. Reading someone else's request is `403`.
- **Double-booking protection** — confirmation writes `reservation_key = resource:date:slot`; the UNIQUE constraint turns a race into `409 "This equipment is already reserved for that slot. Choose another slot."` instead of an overwrite.
- **Retry safety** — `request_key` is supplied by the client, so a retried request returns the existing booking instead of creating a duplicate; a different farmer reusing a key gets `409`.
- **Group stages** — an officer may only advance one stage at a time: `Gathering interest → Coordinating → Scheduled → Completed`. A completed group cannot move.
- **Joining** — only while the group is `Gathering interest` and the date has not passed; joining twice is a no-op.
- **Audit** — every plot creation, booking transition and group change writes an `Activity` row in the same transaction as the change itself.

## AI components
None. Every amount, rate, date and stage is either typed by the farmer or set by a coordinator.

## Dependencies
`farmer_profile` (user + farm profile for `PUT /profile`), `farms` (Farm, FarmCrop), `core` (db, security, audit-through-Activity). Emits nothing to other features today.

## Known limitations
- `Resource` rows are seeded demo data; there is no admin CRUD for the catalogue yet.
- Booking has no notification on confirmation or cancellation — the farmer must refresh.
- `CashEntry.date` and `Booking.date` are stored as strings, not `Date` columns, so date filtering is lexicographic.
- No pagination: lists return everything for the caller.
- Group messaging is a single `description` plus a system-generated `Activity` history — there is no farmer-to-farmer comment thread.
- Rates in the catalogue are indicative; nothing here negotiates or settles payment.

## How to test
No dedicated suite yet. `tests/test_workflows.py` exercises parts of the booking and plot flows. A focused `tests/operations/` package should cover the status-transition matrix, the double-booking race, `request_key` idempotency and the officer-only transitions.
