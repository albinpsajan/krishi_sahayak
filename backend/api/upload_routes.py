"""Upload endpoint: /api/upload (stores files under the configured assets dir)."""

import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, UploadFile

from apps.farmer_profile.models import User
from core.security import get_current_user
from config import settings

uploads_router = APIRouter(prefix="/api", tags=["uploads"])


@uploads_router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOADS_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/uploads/{filename}"
    return {"file_url": file_url, "original_filename": file.filename}
