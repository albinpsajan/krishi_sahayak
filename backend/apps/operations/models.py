"""Relational records for daily farm operations; no request-handling logic."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from core.database import Base


class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    location = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    unit = Column(String, default="hour")
    description = Column(String, default="")


class Booking(Base):
    __tablename__ = "resource_bookings"
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    date = Column(String, nullable=False)
    slot = Column(String, nullable=False)
    notes = Column(String, default="")
    status = Column(String, default="Requested")
    # Reservation key is set only on confirmation. UNIQUE also protects concurrent requests.
    reservation_key = Column(String, unique=True, nullable=True)
    request_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Cooperation(Base):
    __tablename__ = "cooperation_cases"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="Gathering interest")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Participant(Base):
    __tablename__ = "cooperation_participants"
    __table_args__ = (UniqueConstraint("case_id", "farmer_id"),)
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cooperation_cases.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class CashEntry(Base):
    __tablename__ = "cash_entries"
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    crop = Column(String, nullable=False)
    category = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    note = Column(String, default="")


class DocumentCheck(Base):
    __tablename__ = "document_checklist"
    __table_args__ = (UniqueConstraint("farmer_id", "name"),)
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)


class Activity(Base):
    __tablename__ = "operation_activity"
    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
