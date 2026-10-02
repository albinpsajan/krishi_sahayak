"""Image references for MVP uploads; product text is not OCR-extracted yet."""
import os

from fastapi import HTTPException
from config import settings


def validate_image_reference(image_url, farmer_id):
    if not image_url:
        return ""
    prefix = f"/api/input-guard/uploads/{farmer_id}/"
    filename = image_url.removeprefix(prefix)
    if not image_url.startswith(prefix) or len(filename) not in (36, 37) or filename[:32] != filename[:32].lower():
        raise HTTPException(422, "Upload the product photo from this check before submitting it.")
    if not all(char in "0123456789abcdef" for char in filename[:32]) or filename[32:] not in (".jpg", ".png", ".webp"):
        raise HTTPException(422, "Product photo reference is invalid.")
    path = os.path.join(settings.PRIVATE_UPLOADS_DIR, "input-guard", str(farmer_id), filename)
    if not os.path.isfile(path):
        raise HTTPException(422, "That product photo is no longer available. Upload it again before submitting.")
    return image_url
