# Tamper-Evident Audit Ledger

## Purpose
Append-only, cryptographically chained (SHA-256) record of every important action: registrations, case submissions, AI assessments, officer reviews, subsidy decisions. Any modification or deletion breaks the chain and is detectable.

## Inputs
`log_audit_action(db, actor_id, actor_name, actor_role, action, target_type, target_id, metadata)`

## Outputs
- `AuditRecord` row with `prev_hash` / `current_hash`.
- `verify_ledger_integrity(db)` → `{status: VALID|TAMPERED, total_records, corrupted_record_id?}`.

## Main files
| File | Responsibility |
|---|---|
| `apps/audit/audit_ledger.py` | Hash computation, append, integrity walk |
| `apps/audit/models.py` | AuditRecord |
| `api/audit_routes.py` | GET /api/audit/ledger, GET /api/audit/verify |

## Database models
AuditRecord (actor, action, target, timestamp, metadata JSON, prev_hash, current_hash).

## API endpoints
`GET /api/audit/ledger` · `GET /api/audit/verify`

## AI components
None (AI actions are *recorded* with actor_role `AI_SYSTEM`).

## Dependencies
None (features call it; it depends only on core).

## Known limitations
- Single global chain: writes are serialized per commit; high concurrency would need queuing.
- Genesis hash is a constant; production should anchor it externally.

## How to test
```bash
python -m unittest tests.audit.test_audit_ledger -v
```
Covers: valid chain, genesis linkage, sequential linkage, tamper detection with corrupted record id.
