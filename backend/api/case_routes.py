"""Crop case endpoints: /api/cases (list, create, detail, officer review)."""

import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from apps.operations.schemas import StatusInput
from sqlalchemy.orm import Session
from typing import List

from apps.crop_cases.models import AIAssessment, CropCase, CropImage, OfficerReview, Recommendation
from apps.crop_cases.schemas import (
    CropCaseCreate,
    CropCaseResponse,
    OfficerReviewCreate,
    OfficerReviewResponse,
)
from apps.farmer_profile.models import User
from apps.notifications.notification_service import create_notification
from apps.audit.audit_ledger import log_audit_action
from ai.crop_doctor import crop_doctor_ai
from core.database import get_db
from core.errors import AppErrorCode, api_error
from core.logging_config import get_logger
from core.security import get_current_user, require_farmer, require_officer

logger = get_logger("krishi.crop_cases")

cases_router = APIRouter(prefix="/api/cases", tags=["crop_cases"])


def _serialize_case(c: CropCase) -> dict:
    """Shape used by every case endpoint (single place to change)."""
    return {
        "id": c.id,
        "case_number": c.case_number,
        "farmer_id": c.farmer_id,
        "farmer_name": c.farmer.full_name if c.farmer else "Unknown",
        "crop_type": c.crop_type,
        "variety": c.variety,
        "field_location": c.field_location,
        "symptoms_description": c.symptoms_description,
        "status": c.status,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "images": [img.image_url for img in c.images],
        "ai_assessment": c.ai_assessment,
        "officer_review": c.officer_review,
    }


@cases_router.get("", response_model=List[CropCaseResponse])
def get_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Farmers see their own cases; officers see all cases."""
    if current_user.role == "FARMER":
        cases = db.query(CropCase).filter(CropCase.farmer_id == current_user.id).order_by(CropCase.id.desc()).all()
    else:
        cases = db.query(CropCase).order_by(CropCase.id.desc()).all()
    return [_serialize_case(c) for c in cases]


@cases_router.post("", response_model=CropCaseResponse)
def create_crop_case(
    payload: CropCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_farmer),
):
    case_num = f"KS-{uuid.uuid4().hex[:10].upper()}"

    crop_case = CropCase(
        case_number=case_num,
        farmer_id=current_user.id,
        crop_type=payload.crop_type,
        variety=payload.variety or "Local Variety",
        field_location=payload.field_location,
        symptoms_description=payload.symptoms_description,
        status="Awaiting Officer Review",
    )
    db.add(crop_case)
    db.flush()

    image_url = payload.image_base64_or_url or ""
    if image_url:
        if not image_url.startswith(f"/api/uploads/{current_user.id}/"):
            raise api_error(400, AppErrorCode.CASE_ACCESS_DENIED, "Upload a crop photo from your account first")
        db.add(CropImage(case_id=crop_case.id, image_url=image_url))

    ai_assessment = None  # New reports await a human; no fabricated diagnosis.

    log_audit_action(
        db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role="FARMER",
        action="CREATE_CROP_CASE",
        target_type="CROP_CASE",
        target_id=str(crop_case.id),
        metadata={"crop": payload.crop_type, "case_number": case_num},
    )
    create_notification(
        db, user_id=current_user.id,
        title="Crop report received",
        message=f"Report {case_num} is waiting for expert review. You can check its progress in Crop care.",
        malayalam_message="",
        target_link=f"/cases/{crop_case.id}",
    )

    db.commit()
    db.refresh(crop_case)
    logger.info("[CROP_CASE] created case_number=%s farmer_id=%s crop=%s", case_num, current_user.id, payload.crop_type)

    return {
        "id": crop_case.id,
        "case_number": crop_case.case_number,
        "farmer_id": crop_case.farmer_id,
        "farmer_name": current_user.full_name,
        "crop_type": crop_case.crop_type,
        "variety": crop_case.variety,
        "field_location": crop_case.field_location,
        "symptoms_description": crop_case.symptoms_description,
        "status": crop_case.status,
        "created_at": crop_case.created_at,
        "updated_at": crop_case.updated_at,
        "images": [image_url] if image_url else [],
        "ai_assessment": ai_assessment,
        "officer_review": None,
    }


@cases_router.get("/{case_id}", response_model=CropCaseResponse)
def get_case_detail(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(CropCase).filter(CropCase.id == case_id).first()
    if not c:
        raise api_error(404, AppErrorCode.CASE_NOT_FOUND, "Crop case not found")
    if current_user.role == "FARMER" and c.farmer_id != current_user.id:
        raise api_error(403, AppErrorCode.CASE_ACCESS_DENIED, "Access denied")
    return _serialize_case(c)


@cases_router.post("/{case_id}/review", response_model=OfficerReviewResponse)
def submit_officer_review(
    case_id: int,
    payload: OfficerReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    crop_case = db.query(CropCase).filter(CropCase.id == case_id).first()
    if not crop_case:
        raise api_error(404, AppErrorCode.CASE_NOT_FOUND, "Crop case not found")

    existing_review = db.query(OfficerReview).filter(OfficerReview.case_id == case_id).first()
    if existing_review:
        db.delete(existing_review)
        db.flush()

    review = OfficerReview(
        case_id=case_id,
        officer_id=current_user.id,
        is_confirmed=payload.is_confirmed,
        corrected_disease=payload.corrected_disease,
        officer_notes=payload.officer_notes,
        verified_recommendation=payload.verified_recommendation,
        precautions=payload.precautions,
        follow_up_days=payload.follow_up_days,
        malayalam_recommendation=payload.malayalam_recommendation
        or f"കൃഷി ഓഫീസർ നിർദ്ദേശം: {payload.verified_recommendation}",
    )
    db.add(review)

    if payload.recommended_product:
        db.add(
            Recommendation(
                case_id=case_id,
                product_name=payload.recommended_product,
                category=payload.product_category or "Organic Treatment",
                application_dosage=payload.product_dosage or "Standard Dosage",
                timing="As directed by Officer",
            )
        )

    crop_case.status = "Officer Verified"
    db.flush()

    log_audit_action(
        db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role="OFFICER",
        action="VERIFY_CROP_CASE",
        target_type="OFFICER_REVIEW",
        target_id=str(case_id),
        metadata={"is_confirmed": payload.is_confirmed, "corrected_disease": payload.corrected_disease},
    )

    create_notification(
        db,
        user_id=crop_case.farmer_id,
        title="✓ Officer Verified Guidance Issued",
        message=(
            f"Agricultural Officer {current_user.full_name} has verified your case "
            f"{crop_case.case_number}. Check your recommendation."
        ),
        malayalam_message=f"കേസ് {crop_case.case_number}: കൃഷി ഓഫീസർ പരിശോധിച്ചു നിർദ്ദേശം നൽകി.",
        target_link=f"/cases/{case_id}",
    )

    db.commit()
    db.refresh(review)
    logger.info("[CROP_CASE] officer review case_id=%s officer_id=%s confirmed=%s", case_id, current_user.id, payload.is_confirmed)
    return review


@cases_router.patch("/{case_id}/status")
def change_case_status(case_id: int, payload: StatusInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.get(CropCase, case_id)
    if not row:
        raise HTTPException(404, "Report not found")
    if current_user.id != row.farmer_id and current_user.role not in ("OFFICER", "ADMIN"):
        raise HTTPException(403, "This report belongs to another farmer")
    transitions = {"Officer Verified": {"Closed"}, "Closed": {"Awaiting Officer Review"}}
    if payload.status not in transitions.get(row.status, set()):
        raise HTTPException(409, "That transition is not available")
    row.status = payload.status
    log_audit_action(db, actor_id=current_user.id, actor_name=current_user.full_name,
                     actor_role=current_user.role, action="CHANGE_CASE_STATUS", target_type="CROP_CASE",
                     target_id=str(row.id), metadata={"status": row.status})
    db.commit()
    return {"status": row.status}
