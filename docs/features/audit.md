# Tamper-Evident Audit Ledger

## Purpose
Append-only, cryptographically chained (SHA-256) record of every important action: registrations, case submissions, AI assessments, officer reviews, subsidy decisions. Any modification or deletion breaks the chain and is detectable.

## Inputs
`log_audit_action(db, actor_id, actor_name, actor_role, action, target_type, target_id, metadata)`

## Outputs
- `AuditRecord` row with `prev_hash` / `current_hash`, served oldest-first at `GET /api/audit/ledger`.
- `verify_ledger_integrity(db)` → `{status: VALID|TAMPERED, total_records, corrupted_record_id?}`.

## Main files
| File | Responsibility |
|---|---|
| `apps/audit/audit_ledger.py` | Hash computation, append, integrity walk |
| `apps/audit/models.py` | `AuditRecord` (table `audit_records`) |
| `apps/audit/schemas.py` | `AuditRecordResponse` |
| `api/audit_routes.py` | `GET /api/audit/ledger`, `GET /api/audit/verify` |
| `frontend/src/pages/AuditPage.jsx` | Ledger timeline and integrity banner |

## Database models
`AuditRecord` (id, actor_id, actor_name, actor_role `FARMER`/`OFFICER`/`AI_SYSTEM`, action, target_type, target_id as string, timestamp, `metadata_json`, prev_hash, current_hash).

## API endpoints
`GET /api/audit/ledger` (any authenticated user) · `GET /api/audit/verify` (public).

## Who writes to the ledger
`core/seed_data.py` and `api/case_routes.py` write entries today (`CREATE_CROP_CASE`, `GENERATE_AI_ASSESSMENT`, `VERIFY_CROP_CASE`, `CHANGE_CASE_STATUS`). The `operations` feature keeps its own `Activity` table for group and booking history instead of using the hash chain — see [`operations.md`](operations.md).

## AI components
None (AI actions are *recorded* with actor_role `AI_SYSTEM`).

## Dependencies
None (features call it; it depends only on core).

## Known limitations
- Single global chain: writes are serialized per commit; high concurrency would need queuing.
- Genesis hash is a constant; production should anchor it externally.
- The chain detects modification of existing rows but cannot prevent deletion of the **last** entry, and there is no periodic external anchoring.
- `metadata_json` is stored as `Text`, not a JSON column, so it is not queryable.
- `GET /api/audit/verify` is unauthenticated — anyone can probe the chain, which is convenient for the pilot but should be officer-only in production.
- Two features keep separate histories (`audit_records` and `operation_activity`), so a complete activity view needs both.

## How to test
```bash
python -m unittest tests.audit.test_audit_ledger -v
```
Covers: valid chain, genesis linkage, sequential linkage, tamper detection with corrupted record id.
