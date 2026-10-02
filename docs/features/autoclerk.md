# AutoClerk — Official Report Engine

## Purpose
Synthesizes the structured administrative report (markdown) for the Agricultural Officer from existing case data. **Formatting only — it invents no facts.**

## Inputs
Crop case, farmer context (via `profile_service`), AI assessment, officer review, optional subsidy application.

## Outputs
`{report_id, case_number, title, generated_at, content_markdown, is_finalized}`

## Main files
| File | Responsibility |
|---|---|
| `apps/autoclerk/autoclerk_service.py` | Markdown report synthesis |
| `api/officer_routes.py` | GET /api/officer/autoclerk/{case_id} |

## Database models
None of its own (reads other features' rows).

## API endpoints
`GET /api/officer/autoclerk/{case_id}` (officer only)

## AI components
None (the AI assessment is an *input*, already stored).

## Dependencies
crop_cases (case + assessments), farmer_profile (farmer facts), core guards.

## Known limitations
- Final sign-off is UI-only (alert); persisted signatures are future work.

## How to test
```bash
python -m unittest tests.autoclerk.test_autoclerk -v
```
