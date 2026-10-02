"""Officer endpoints: /api/officer (AutoClerk report generation)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.autoclerk.autoclerk_service import generate_autoclerk_report
from apps.crop_cases.models import CropCase
from apps.farmer_profile.profile_service import get_farmer_context
from core.database import get_db
from core.errors import AppErrorCode, api_error
from core.security import require_officer

officer_router = APIRouter(prefix="/api/officer", tags=["officer"])


@officer_router.get("/autoclerk/{case_id}")
def get_autoclerk_report(case_id: int, db: Session = Depends(get_db), current_user=Depends(require_officer)):
    crop_case = db.query(CropCase).filter(CropCase.id == case_id).first()
    if not crop_case:
        raise api_error(404, AppErrorCode.CASE_NOT_FOUND, "Case not found")

    # Farmer facts via the profile service (single source of truth)
    farmer_ctx = get_farmer_context(db, crop_case.farmer)
    farmer_dict = {
        "full_name": farmer_ctx["full_name"],
        "phone": farmer_ctx["phone"],
        "district": farmer_ctx["district"],
    }
    crop_dict = {
        "case_number": crop_case.case_number,
        "crop_type": crop_case.crop_type,
        "field_location": crop_case.field_location,
        "symptoms_description": crop_case.symptoms_description,
    }

    ai_dict = None
    if crop_case.ai_assessment:
        ai_dict = {
            "probable_disease": crop_case.ai_assessment.probable_disease,
            "confidence": crop_case.ai_assessment.confidence,
            "observations": crop_case.ai_assessment.observations,
        }

    off_dict = None
    if crop_case.officer_review:
        off_dict = {
            "is_confirmed": crop_case.officer_review.is_confirmed,
            "corrected_disease": crop_case.officer_review.corrected_disease,
            "officer_notes": crop_case.officer_review.officer_notes,
            "verified_recommendation": crop_case.officer_review.verified_recommendation,
        }

    return generate_autoclerk_report(
        crop_case=crop_dict,
        farmer=farmer_dict,
        ai_assessment=ai_dict,
        officer_review=off_dict,
    )
