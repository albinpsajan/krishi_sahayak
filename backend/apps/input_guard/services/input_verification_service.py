"""Officer decision workflow for submitted product checks."""
from datetime import datetime

from fastapi import HTTPException


def review_check(db, check, officer, decision, note):
    if check.status in ("Approved", "Not recommended", "Field visit required"):
        raise HTTPException(409, "This check already has a final decision.")
    if check.status not in ("Submitted", "Under review", "More details needed"):
        raise HTTPException(409, "This check is not awaiting review.")
    check.status = decision
    check.officer_id = officer.id
    check.officer_name = officer.full_name
    check.officer_note = note.strip()
    check.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(check)
    return check
