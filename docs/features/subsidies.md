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
| `api/subsidy_routes.py` | HTTP endpoints (list schemes, apply, list applications, decide) |
| `apps/subsidies/services/subsidy_matcher.py` | Orchestrates rules → risk classification |
| `apps/subsidies/services/eligibility_checker.py` | Deterministic rules (crop category, land ceiling, case verification) |
| `apps/subsidies/services/document_checker.py` | Missing-document detection (token-overlap matching) |
| `apps/subsidies/models.py` | SubsidyScheme, SubsidyApplication, ApplicationDocument |
| `apps/subsidies/schemas.py` | Request/response contracts |
| `frontend/src/pages/SubsidiesPage.jsx` | Scheme list, application form, application status |

## Database models
- **SubsidyScheme** — officer-managed source of truth (criteria, documents, amounts, max subsidy).
- **SubsidyApplication** — farmer application + rule engine output + officer decision.
- **ApplicationDocument** — attached document per application.

## API endpoints
`GET /api/subsidies` (public scheme directory) · `POST /api/subsidies/apply` (farmer) · `GET /api/subsidies/applications` · `POST /api/subsidies/applications/{id}/decide` (officer).

## Debug map

| Symptom | File to open |
|---|---|
| Wrong subsidy match / risk level | `apps/subsidies/services/subsidy_matcher.py` |
| Wrong eligibility verdict | `apps/subsidies/services/eligibility_checker.py` |
| Wrong missing-document list | `apps/subsidies/services/document_checker.py` |
| Wrong application prefill or request shape | `api/subsidy_routes.py` |
| Wrong deadline or scheme facts | `apps/subsidies/models.py` (officer-managed data) |

## AI components
None by design. Explanations shown to farmers come from rule output text produced by the deterministic services.

## Dependencies
`profile_service` (farmer facts), `audit_ledger` (application + decision records), `notification_service` (decision alerts), `farmer_profile` (auth).

## Known limitations
- Document upload is currently a demo attachment; real file intake is a future branch.
- Deadlines are not yet modeled on schemes (planned `deadline_notifications.py`).
- Land ceiling is a fixed 10-acre rule; per-scheme thresholds are future work.
- The scheme directory is public, so any client can enumerate scheme criteria and amounts; that is intentional for transparency but should be revisited before real deployment.
- Document matching is token-overlap on the scheme's document string, so a document named slightly differently is reported missing.
- Nothing expires or withdraws an application, and there is no revision path after an `Info Requested` decision — the farmer must submit again.

## How to test
```bash
python -m unittest discover -s tests -t . -v               # everything
python -m unittest tests.subsidies.test_matching -v        # matching and risk level
python -m unittest tests.subsidies.test_eligibility -v     # eligibility rules
python -m unittest tests.subsidies.test_documents -v       # document detection
```
Covered: eligible → fast-track, crop mismatch → review, missing docs → incomplete, large holding → review (never fast-track), combined uploads, officer-verified case bonus.
