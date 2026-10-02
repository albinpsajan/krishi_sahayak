"""Private crop photo storage with authenticated access and bounded image uploads."""
import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from core.security import get_current_user
from config import settings

uploads_router = APIRouter(prefix="/api", tags=["uploads"])


@uploads_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    content = await file.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "Choose a photo smaller than 5 MB")
    ext = ".jpg" if content.startswith(b"\xff\xd8\xff") else ".png" if content.startswith(b"\x89PNG\r\n\x1a\n") else None
    if not ext:
        raise HTTPException(415, "Only JPEG and PNG crop photographs are accepted")
    filename = uuid.uuid4().hex + ext
    folder = os.path.join(settings.PRIVATE_UPLOADS_DIR, str(user.id))
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), "wb") as output:
        output.write(content)
    return {"file_url": f"/api/uploads/{user.id}/{filename}"}


@uploads_router.get("/uploads/{owner_id}/{filename}")
def read_photo(owner_id: int, filename: str, user=Depends(get_current_user)):
    if user.id != owner_id and user.role not in ("OFFICER", "ADMIN"):
        raise HTTPException(403, "You cannot view this photo")
    if len(filename) != 36 or not filename.endswith((".jpg", ".png")) or not all(c in "0123456789abcdef" for c in filename[:32]):
        raise HTTPException(404, "Photo not found")
    path = os.path.join(settings.PRIVATE_UPLOADS_DIR, str(owner_id), filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "Photo not found")
    return FileResponse(path, headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})
