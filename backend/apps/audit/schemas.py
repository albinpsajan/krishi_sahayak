"""Pydantic schema for audit ledger endpoints."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class AuditRecordResponse(BaseModel):
    id: int
    actor_id: int
    actor_name: str
    actor_role: str
    action: str
    target_type: str
    target_id: str
    timestamp: datetime
    metadata_json: Optional[str]
    prev_hash: str
    current_hash: str

    class Config:
        from_attributes = True
