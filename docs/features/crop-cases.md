# Crop Cases & CropDoctor

## Purpose
Farmers submit crop-health cases with a photo; the AI layer produces a **preliminary** assessment; the Agricultural Officer verifies or corrects it (human-in-the-loop). The officer's verified recommendation always supersedes the AI.

## Inputs
- Case form: crop type, variety, field location, symptoms text, leaf photo (uploaded via `/api/upload`).

## Outputs
- CropCase with status flow: `Submitted → Awaiting Officer Review → Officer Verified`.
- AIAssessment (preliminary) + OfficerReview (authoritative) + optional product Recommendation.
- Farmer notifications (English + Malayalam) at each step.

## Main files
| File | Responsibility |
|---|---|
| `api/case_routes.py` | Case endpoints + officer review endpoint |
| `apps/crop_cases/models.py` | CropCase, CropImage, AIAssessment, OfficerReview, Recommendation |
| `ai/crop_doctor.py` | Preliminary assessment provider |
| `ai/knowledge_base.py` | Disease data + Malayalam translations |

## Database models
CropCase, CropImage, AIAssessment, OfficerReview, Recommendation (all in `apps/crop_cases/models.py`).

## API endpoints
`GET/POST /api/cases` · `GET /api/cases/{id}` · `POST /api/cases/{id}/review`

## AI components
`ai/crop_doctor.py` (knowledge-base vision provider; external provider hook via `CROP_DOCTOR_API_KEY`). Audit-logged as actor `AI_SYSTEM`, actor_id 1.

## Dependencies
`audit_ledger`, `notification_service`, `auth` guards (farmer creates, officer reviews).

## Known limitations
- Local knowledge base covers 5 demo crops; a real model integration is future work.
- One AI assessment per case (unique case_id).

## How to test
```bash
python -m unittest tests.ai.test_crop_doctor -v
```
