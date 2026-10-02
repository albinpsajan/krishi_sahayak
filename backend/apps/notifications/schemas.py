"""Pydantic schema for notification endpoints."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    malayalam_message: Optional[str] = None
    is_read: bool
    notification_type: str
    target_link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
