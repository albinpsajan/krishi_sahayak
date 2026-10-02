# SubsidyChain — Personalized Subsidy Module

## Purpose
Discover subsidy schemes for a farmer, screen applications with **deterministic** eligibility rules, and route them to the Agricultural Officer with a risk classification. The officer holds sole decision authority; the AI layer never decides subsidy outcomes.

## Inputs
- Farmer profile facts (land size, crops) via `profile_service.get_farmer_context()` — never duplicated.
- Scheme record (crop category, required documents, amounts) — officer-managed data in `subsidy_schemes`.
- Optional linked crop case (for officer-verified diagnostic proof).

## Outputs
- Application with `risk_level`: `LOW_RISK_FAST_TRACK` | `HUMAN_REVIEW_REQUIRED` | `INCOMPLETE_DOCUMENTS`
- JSON `rule_engine_output` (score, rules passed, flags, missing documents) stored on the application.

## Main files
| File | Responsibility |
|---|---|
| `api/subsidy_routes.py` | HTTP endpoints (apply, list, decide) |
| `services/subsidy_matcher.py` | Orchestrates rules → risk classification |
| `services/eligibility_checker.py` | Deterministic rules (crop category, land ceiling, case verification) |
| `services/document_checker.py` | Missing-document detection (token-overlap matching) |
| `models.py` | SubsidyScheme, SubsidyApplication, ApplicationDocument |

## Database models
- **SubsidyScheme** — officer-managed source of truth (criteria, documents, amounts).
- **SubsidyApplication** — farmer application + rule engine output + officer decision.
- **ApplicationDocument** — attached document per application.

## API endpoints
`GET /api/subsidies` · `POST /api/subsidies/apply` · `GET /api/subsidies/applications` · `POST /api/subsidies/applications/{id}/decide`

## AI components
None by design. Explanations shown to farmers come from rule output text produced by the deterministic services.

## Dependencies
`profile_service` (farmer facts), `audit_ledger` (application + decision records), `notification_service` (decision alerts).

## Known limitations
- Document upload is currently a demo attachment; real file intake is a future branch.
- Deadlines are not yet modeled on schemes (planned `deadline_notifications.py`).
- Land ceiling is a fixed 10-acre rule; per-scheme thresholds are future work.

## How to test
```bash
python -m unittest discover -s tests -t . -v          # everything
python -m unittest tests.subsidies.test_matching -v   # just matching
python -m unittest tests.subsidies.test_documents -v  # just documents
```
Covered: eligible → fast-track, crop mismatch → review, missing docs → incomplete, large holding → review (never fast-track), combined uploads, officer-verified case bonus.
