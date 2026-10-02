"""Authenticated farmer and officer endpoints for Input Guard."""
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apps.input_guard.models import InputCheck
from apps.input_guard.schemas import InputCheckCreate, InputReview
from apps.input_guard.services.input_guard_service import create_check, input_check_view, update_check
from apps.input_guard.services.input_verification_service import review_check
from config import settings
from core.database import get_db
from core.security import get_current_user, require_farmer, require_officer

router = APIRouter(prefix="/api/input-guard", tags=["input guard"])


@router.get("")
def list_checks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(InputCheck)
    if user.role == "FARMER":
        query = query.filter(InputCheck.farmer_id == user.id)
    return [input_check_view(row) for row in query.order_by(InputCheck.created_at.desc()).all()]


@router.post("/check", status_code=201)
def submit_check(payload: InputCheckCreate, db: Session = Depends(get_db), farmer=Depends(require_farmer)):
    return input_check_view(create_check(db, farmer, payload))


@router.patch("/{input_id}")
def resubmit_check(input_id: int, payload: InputCheckCreate, db: Session = Depends(get_db), farmer=Depends(require_farmer)):
    row = db.get(InputCheck, input_id)
    if not row or row.farmer_id != farmer.id:
        raise HTTPException(404, "Input check not found.")
    try:
        return input_check_view(update_check(db, row, farmer, payload))
    except ValueError as error:
        raise HTTPException(409, str(error))


@router.post("/upload")
async def upload_product_photo(file: UploadFile = File(...), farmer=Depends(require_farmer)):
    content = await file.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "Choose a product photo smaller than 5 MB.")
    if content.startswith(b"\xff\xd8\xff"):
        ext = ".jpg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        ext = ".png"
    elif content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        ext = ".webp"
    else:
        raise HTTPException(415, "Use a JPEG, PNG, or WebP product photo.")
    filename = uuid.uuid4().hex + ext
    folder = os.path.join(settings.PRIVATE_UPLOADS_DIR, "input-guard", str(farmer.id))
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "wb") as output:
        output.write(content)
    return {"image_url": f"/api/input-guard/uploads/{farmer.id}/{filename}"}


@router.get("/uploads/{owner_id}/{filename}")
def read_product_photo(owner_id: int, filename: str, user=Depends(get_current_user)):
    if user.id != owner_id and user.role not in ("OFFICER", "ADMIN"):
        raise HTTPException(403, "You cannot view this product photo.")
    ext = os.path.splitext(filename)[1]
    if ext not in (".jpg", ".png", ".webp") or len(filename) != 32 + len(ext) or not all(char in "0123456789abcdef" for char in filename[:32]):
        raise HTTPException(404, "Photo not found.")
    path = os.path.join(settings.PRIVATE_UPLOADS_DIR, "input-guard", str(owner_id), filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "Photo not found.")
    media_type = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}[ext]
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/officer/pending")
def pending_checks(db: Session = Depends(get_db), officer=Depends(require_officer)):
    rows = db.query(InputCheck).filter(InputCheck.status.in_(("Submitted", "Under review", "More details needed"))).order_by(InputCheck.created_at.asc()).all()
    return [input_check_view(row) for row in rows]


@router.patch("/officer/{input_id}/review")
def review(input_id: int, payload: InputReview, db: Session = Depends(get_db), officer=Depends(require_officer)):
    row = db.get(InputCheck, input_id)
    if not row:
        raise HTTPException(404, "Input check not found.")
    return input_check_view(review_check(db, row, officer, payload.decision, payload.note))
