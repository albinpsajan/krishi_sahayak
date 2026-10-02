# Crop Cases & CropDoctor

## Purpose
Farmers submit crop-health cases with a photo; the AI layer produces a **preliminary** assessment; the Agricultural Officer verifies or corrects it (human-in-the-loop). The officer's verified recommendation always supersedes the AI.

## Inputs
- Case form: crop type, variety, field location, symptoms text, leaf photo (uploaded via `/api/upload`).

## Outputs
- CropCase with status flow: `Awaiting Officer Review` (set on create) → `Officer Verified` (set by the review endpoint) → `Closed`, and `Closed` → `Awaiting Officer Review` to reopen.
- AIAssessment (preliminary) + OfficerReview (authoritative) + optional product Recommendation.
- Farmer notifications (English + Malayalam) at each step.

## Main files
| File | Responsibility |
|---|---|
| `api/case_routes.py` | Case endpoints, officer review endpoint, status transitions, audit writes |
| `apps/crop_cases/models.py` | CropCase, CropImage, AIAssessment, OfficerReview, Recommendation |
| `apps/crop_cases/schemas.py` | Request/response contracts |
| `ai/crop_doctor.py` | Preliminary assessment provider |
| `ai/knowledge_base.py` | Disease data + Malayalam translations |
| `api/upload_routes.py` | Private photo storage the case form uploads to |
| `frontend/src/pages/CasesPage.jsx`, `CropCarePage.jsx` | Case list and case care views |
| `frontend/src/components/CropCaseWizardModal.jsx`, `CaseDetailModal.jsx`, `CropReportForm.jsx`, `ReportDetail.jsx` | Submission and review UI |

## Database models
CropCase, CropImage, AIAssessment, OfficerReview, Recommendation (all in `apps/crop_cases/models.py`).

## API endpoints
`GET /api/cases` · `POST /api/cases` (farmer) · `GET /api/cases/{id}` · `POST /api/cases/{id}/review` (officer) · `PATCH /api/cases/{id}/status`.

## Ownership and status rules
- A farmer may only read and transition their own case; anyone else gets `403` on a foreign case.
- `PATCH /{id}/status` accepts only `Officer Verified → Closed` and `Closed → Awaiting Officer Review`. Any other move is `409` — a case can never be skipped straight from submission to closed, and the farmer cannot mark their own case verified.
- Every status change writes a `CHANGE_CASE_STATUS` audit entry with the actor's real role.

## AI components
`ai/crop_doctor.py` (knowledge-base vision provider; external provider hook via `CROP_DOCTOR_API_KEY`). Audit-logged as actor `AI_SYSTEM`, actor_id 1.

## Dependencies
`audit_ledger`, `notification_service`, `farmer_profile` (via `profile_service`), `auth` guards (farmer creates, officer reviews), `api/upload_routes.py` for the photo.

## Known limitations
- Local knowledge base covers 5 demo crops; a real model integration is future work.
- One AI assessment per case (unique case_id).
- `GET /api/cases/{id}` returns the case without a per-field ownership filter beyond the owner/officer check, so it relies entirely on the guard in the router.
- Status changes raise a plain `HTTPException` (`409`), so this feature's error shape is not the `core/errors.py` envelope used elsewhere.
- No case deletion, no file attachments other than the crop photo, and no re-assessment after a change.
- The review endpoint does not verify that the officer actually visited the field; it is an attestation, not a geospatial check.

## How to test
```bash
python -m unittest tests.ai.test_crop_doctor -v
```
