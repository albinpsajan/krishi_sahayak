"""
Subsidy models: SubsidyScheme, SubsidyApplication, ApplicationDocument.

The scheme table is the officer-managed source of truth for amounts, criteria
and deadlines. The rule engine NEVER invents these values (docs/architecture.md
section 3).
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class SubsidyScheme(Base):
    __tablename__ = "subsidy_schemes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    hindi_malayalam_name = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    crop_category = Column(String, nullable=False)  # Paddy, Spices, All Crops, Organic
    eligibility_criteria = Column(Text, nullable=False)
    required_documents = Column(Text, nullable=False)
    benefit_information = Column(String, nullable=False)
    max_subsidy_amount = Column(Float, default=10000.0)

    applications = relationship("SubsidyApplication", back_populates="scheme")


class SubsidyApplication(Base):
    __tablename__ = "subsidy_applications"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String, unique=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("subsidy_schemes.id"), nullable=False)
    crop_case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=True)
    status = Column(String, default="Submitted")
    # Statuses: Application Created, Submitted, Rule Screening, Officer Review, Approved, Rejected, Info Requested

    risk_level = Column(String, default="HUMAN_REVIEW_REQUIRED")
    # Values: LOW_RISK_FAST_TRACK, HUMAN_REVIEW_REQUIRED, INCOMPLETE_DOCUMENTS
    rule_engine_output = Column(Text, nullable=True)  # JSON summary of rule evaluation
    requested_subsidy_amount = Column(Float, default=5000.0)
    approved_subsidy_amount = Column(Float, nullable=True)
    officer_decision_notes = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("User", back_populates="subsidy_applications")
    scheme = relationship("SubsidyScheme", back_populates="applications")
    crop_case = relationship("CropCase", back_populates="subsidy_applications")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("subsidy_applications.id"), nullable=False)
    document_type = Column(String, nullable=False)  # Land Record, Aadhaar, Crop Health Certificate
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("SubsidyApplication", back_populates="documents")
