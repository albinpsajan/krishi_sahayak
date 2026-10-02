"""Profile endpoint: /api/profile (single source of truth via profile_service)."""

from fastapi import APIRouter, Depends

from apps.farmer_profile.models import User
from apps.farmer_profile.profile_service import build_profile_response
from core.database import get_db
from core.security import get_current_user

profile_router = APIRouter(prefix="/api", tags=["profile"])


@profile_router.get("/profile")
def get_profile(db=Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_profile_response(current_user)
