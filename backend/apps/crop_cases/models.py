"""
Crop case models: CropCase, CropImage, AIAssessment, OfficerReview, Recommendation.

The AI assessment is stored separately from the officer review so the officer's
verified answer always supersedes the preliminary AI diagnosis
(docs/architecture.md section 3).
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class CropCase(Base):
    __tablename__ = "crop_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_type = Column(String, nullable=False)  # e.g. Paddy, Tomato, Wheat, Pepper
    variety = Column(String, nullable=True)
    field_location = Column(String, nullable=False)
    symptoms_description = Column(Text, nullable=True)
    status = Column(String, default="Submitted")
    # Statuses: Draft, Submitted, AI Processing, Awaiting Officer Review, Officer Verified, Recommendation Available, Closed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("User", back_populates="crop_cases")
    images = relationship("CropImage", back_populates="crop_case", cascade="all, delete-orphan")
    ai_assessment = relationship("AIAssessment", back_populates="crop_case", uselist=False, cascade="all, delete-orphan")
    officer_review = relationship("OfficerReview", back_populates="crop_case", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="crop_case", cascade="all, delete-orphan")
    subsidy_applications = relationship("SubsidyApplication", back_populates="crop_case")


class CropImage(Base):
    __tablename__ = "crop_images"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=False)
    image_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    crop_case = relationship("CropCase", back_populates="images")


class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=False, unique=True)
    probable_disease = Column(String, nullable=False)
    hindi_malayalam_name = Column(String, nullable=True)  # Malayalam/Hindi diagnosis name
    confidence = Column(Float, nullable=False)  # e.g. 88.5
    observations = Column(Text, nullable=False)
    preliminary_guidance = Column(Text, nullable=False)
    malayalam_guidance = Column(Text, nullable=True)  # Unicode Malayalam translation
    raw_ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    crop_case = relationship("CropCase", back_populates="ai_assessment")


class OfficerReview(Base):
    __tablename__ = "officer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=False, unique=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_confirmed = Column(Boolean, default=True)  # True if AI diagnosis confirmed, False if corrected
    corrected_disease = Column(String, nullable=True)
    officer_notes = Column(Text, nullable=True)
    verified_recommendation = Column(Text, nullable=False)
    precautions = Column(Text, nullable=True)
    follow_up_days = Column(Integer, default=7)
    malayalam_recommendation = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    crop_case = relationship("CropCase", back_populates="officer_review")
    officer = relationship("User")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=False)
    product_name = Column(String, nullable=False)  # e.g. Trichoderma viride / Neem Oil 10000 PPM
    category = Column(String, nullable=False)  # Organic Fungicide, Chemical Remedy, Fertilizer
    application_dosage = Column(String, nullable=False)  # e.g. 5ml / Litre water
    timing = Column(String, nullable=False)  # Spray early morning
    guidance_notes = Column(Text, nullable=True)

    crop_case = relationship("CropCase", back_populates="recommendations")
