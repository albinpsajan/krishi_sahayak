"""AuditRecord model: one entry in the tamper-evident hash chain."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from core.database import Base


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=False)
    actor_name = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)  # FARMER, OFFICER, AI_SYSTEM
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)  # CROP_CASE, SUBSIDY_APP, OFFICER_REVIEW
    target_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, nullable=True)
    prev_hash = Column(String, nullable=False)
    current_hash = Column(String, nullable=False)
