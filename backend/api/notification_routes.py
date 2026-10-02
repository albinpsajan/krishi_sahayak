"""Notification endpoints: /api/notifications (list, mark read)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from apps.farmer_profile.models import User
from apps.notifications.models import Notification
from apps.notifications.schemas import NotificationResponse
from core.database import get_db
from core.security import get_current_user

notifications_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notifications_router.get("", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.id.desc())
        .all()
    )


@notifications_router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if notif:
        notif.is_read = True
        db.commit()
    return {"status": "success"}
