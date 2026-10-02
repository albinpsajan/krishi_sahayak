"""
User, FarmerProfile and OfficerProfile models.

One responsibility: identity + profile persistence. Authentication logic lives
in core/security.py; profile retrieval logic lives in profile_service.py.
Cross-feature relationships use class-name strings so features stay decoupled.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)  # login handle
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=True)  # collected during post-signup onboarding
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # FARMER, OFFICER, ADMIN
    phone = Column(String, nullable=True)
    language = Column(String, default="en")  # en, ml (Malayalam)
    profile_completed = Column(Boolean, default=False)  # False until onboarding details submitted
    created_at = Column(DateTime, default=datetime.utcnow)

    # String targets are resolved against the shared SQLAlchemy registry,
    # so this module does not import other feature packages.
    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False)
    officer_profile = relationship("OfficerProfile", back_populates="user", uselist=False)
    crop_cases = relationship("CropCase", back_populates="farmer")
    subsidy_applications = relationship("SubsidyApplication", back_populates="farmer")
    notifications = relationship("Notification", back_populates="user")
    farms = relationship("Farm", back_populates="farmer")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    district = Column(String, default="Palakkad")
    state = Column(String, default="Kerala")
    land_size_acres = Column(Float, default=2.5)
    primary_crops = Column(String, default="Paddy, Coconut, Spices")
    water_source = Column(String, default="Canal & Borewell")
    kissan_credit_card = Column(Boolean, default=True)

    user = relationship("User", back_populates="farmer_profile")


class OfficerProfile(Base):
    __tablename__ = "officer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    officer_code = Column(String, unique=True, index=True)
    designation = Column(String, default="Senior Agricultural Officer")
    jurisdiction_district = Column(String, default="Palakkad District")
    department = Column(String, default="Department of Agriculture & Farmers Welfare")

    user = relationship("User", back_populates="officer_profile")
