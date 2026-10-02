"""Subsidy endpoints: /api/subsidies (schemes, apply, applications, decide)."""

import json
import random

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from apps.audit.audit_ledger import log_audit_action
from apps.crop_cases.models import CropCase
from apps.farmer_profile.models import User
from apps.farmer_profile.profile_service import get_farmer_context
from apps.notifications.notification_service import create_notification
from apps.subsidies.models import ApplicationDocument, SubsidyApplication, SubsidyScheme
from apps.subsidies.schemas import (
    SubsidyApplicationCreate,
    SubsidyApplicationResponse,
    SubsidyDecision,
    SubsidySchemeResponse,
)
from apps.subsidies.services.subsidy_matcher import evaluate_subsidy_application
from core.database import get_db
from core.errors import AppErrorCode, api_error
from core.logging_config import get_logger
from core.security import get_current_user, require_farmer, require_officer

logger = get_logger("krishi.subsidies")

subsidies_router = APIRouter(prefix="/api/subsidies", tags=["subsidies"])


def _serialize_application(a: SubsidyApplication) -> dict:
    return {
        "id": a.id,
        "application_number": a.application_number,
        "farmer_id": a.farmer_id,
        "farmer_name": a.farmer.full_name if a.farmer else "Unknown",
        "scheme_id": a.scheme_id,
        "scheme_name": a.scheme.name if a.scheme else "Scheme",
        "crop_case_id": a.crop_case_id,
        "status": a.status,
        "risk_level": a.risk_level,
        "rule_engine_output": a.rule_engine_output,
        "requested_subsidy_amount": a.requested_subsidy_amount,
        "approved_subsidy_amount": a.approved_subsidy_amount,
        "officer_decision_notes": a.officer_decision_notes,
        "applied_at": a.applied_at,
    }


@subsidies_router.get("", response_model=List[SubsidySchemeResponse])
def get_subsidies(db: Session = Depends(get_db)):
    return db.query(SubsidyScheme).all()


@subsidies_router.post("/apply", response_model=SubsidyApplicationResponse)
def apply_for_subsidy(
    payload: SubsidyApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_farmer),
):
    scheme = db.query(SubsidyScheme).filter(SubsidyScheme.id == payload.scheme_id).first()
    if not scheme:
        raise api_error(404, AppErrorCode.SCHEME_NOT_FOUND, "Subsidy scheme not found")

    # Farmer facts always come from the profile service (single source of truth)
    farmer_ctx = get_farmer_context(db, current_user)
    profile_dict = {
        "land_size_acres": farmer_ctx["land_size_acres"],
        "primary_crops": farmer_ctx["primary_crops"],
    }

    crop_case_dict = None
    if payload.crop_case_id:
        crop_case = db.query(CropCase).filter(CropCase.id == payload.crop_case_id).first()
        if crop_case:
            crop_case_dict = {"crop_type": crop_case.crop_type, "status": crop_case.status}

    # Deterministic SubsidyChain rule engine evaluation (never AI-decided)
    eval_result = evaluate_subsidy_application(
        farmer_profile=profile_dict,
        scheme={"crop_category": scheme.crop_category, "required_documents": scheme.required_documents},
        application_docs=[{"document_type": "Aadhaar Card"}, {"document_type": "Land Possession Certificate"}],
        crop_case=crop_case_dict,
    )

    app_num = f"SUB-2026-{random.randint(10000, 99999)}"
    subsidy_app = SubsidyApplication(
        application_number=app_num,
        farmer_id=current_user.id,
        scheme_id=payload.scheme_id,
        crop_case_id=payload.crop_case_id,
        status="Rule Screening",
        risk_level=eval_result["risk_level"],
        rule_engine_output=json.dumps(eval_result),
        requested_subsidy_amount=payload.requested_subsidy_amount,
    )
    db.add(subsidy_app)
    db.flush()

    # Demo document attachment
    db.add(
        ApplicationDocument(
            application_id=subsidy_app.id,
            document_type="Aadhaar Card & Land Certificate",
            file_path="documents/verified_land_record.pdf",
        )
    )

    log_audit_action(
        db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role="FARMER",
        action="SUBMIT_SUBSIDY_APPLICATION",
        target_type="SUBSIDY_APP",
        target_id=str(subsidy_app.id),
        metadata={"scheme_id": scheme.id, "scheme_name": scheme.name, "risk_level": eval_result["risk_level"]},
    )

    db.commit()
    db.refresh(subsidy_app)
    return _serialize_application(subsidy_app)


@subsidies_router.get("/applications", response_model=List[SubsidyApplicationResponse])
def get_subsidy_applications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "FARMER":
        apps = (
            db.query(SubsidyApplication)
            .filter(SubsidyApplication.farmer_id == current_user.id)
            .order_by(SubsidyApplication.id.desc())
            .all()
        )
    else:
        apps = db.query(SubsidyApplication).order_by(SubsidyApplication.id.desc()).all()
    return [_serialize_application(a) for a in apps]


@subsidies_router.post("/applications/{application_id}/decide", response_model=SubsidyApplicationResponse)
def decide_subsidy_application(
    application_id: int,
    payload: SubsidyDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    sub_app = db.query(SubsidyApplication).filter(SubsidyApplication.id == application_id).first()
    if not sub_app:
        raise api_error(404, AppErrorCode.APPLICATION_NOT_FOUND, "Application not found")

    sub_app.status = payload.status  # Approved, Rejected, Info Requested
    if payload.status == "Approved":
        sub_app.approved_subsidy_amount = payload.approved_amount or sub_app.requested_subsidy_amount
    sub_app.officer_decision_notes = payload.decision_notes

    log_audit_action(
        db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role="OFFICER",
        action=f"SUBSIDY_DECISION_{payload.status.upper()}",
        target_type="SUBSIDY_APP",
        target_id=str(application_id),
        metadata={
            "decision": payload.status,
            "approved_amount": sub_app.approved_subsidy_amount,
            "notes": payload.decision_notes,
        },
    )

    create_notification(
        db,
        user_id=sub_app.farmer_id,
        title=f"Subsidy Application Status: {payload.status}",
        message=f"Application {sub_app.application_number} decision: {payload.status}. {payload.decision_notes}",
        malayalam_message=f"സബ്‌സിഡി അപേക്ഷ {sub_app.application_number}: തീരുമാനമെടുത്തു ({payload.status}).",
        target_link="/subsidies",
    )

    db.commit()
    db.refresh(sub_app)
    logger.info(
        "[SUBSIDY_DECISION] application=%s officer_id=%s decision=%s",
        sub_app.application_number,
        current_user.id,
        payload.status,
    )
    return _serialize_application(sub_app)

