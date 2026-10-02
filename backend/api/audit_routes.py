"""Audit endpoints: /api/audit (ledger timeline, integrity check)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from apps.audit.audit_ledger import verify_ledger_integrity
from apps.audit.models import AuditRecord
from apps.audit.schemas import AuditRecordResponse
from core.database import get_db
from core.security import get_current_user

audit_router = APIRouter(prefix="/api/audit", tags=["audit"])


@audit_router.get("/ledger", response_model=List[AuditRecordResponse])
def get_audit_ledger(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(AuditRecord).order_by(AuditRecord.id.asc()).all()


@audit_router.get("/verify")
def verify_audit_ledger(db: Session = Depends(get_db)):
    return verify_ledger_integrity(db)
