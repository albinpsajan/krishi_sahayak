"""Persistence models for explainable plantation and irrigation plans."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from core.database import Base


class SmartPlot(Base):
    __tablename__ = "smart_plots"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plot_name = Column(String, nullable=False)
    village = Column(String, nullable=True)
    district = Column(String, nullable=True)
    boundary_json = Column(Text, nullable=False)
    area_sq_m = Column(Float, nullable=False)
    area_acres = Column(Float, nullable=False)
    area_cents = Column(Float, nullable=False)
    area_hectares = Column(Float, nullable=False)
    shape_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SmartPlan(Base):
    __tablename__ = "smart_plans"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plot_id = Column(Integer, ForeignKey("smart_plots.id"), nullable=False, index=True)
    main_crop = Column(String, nullable=False)
    water_source = Column(String, nullable=False)
    soil_type = Column(String, nullable=False)
    budget_level = Column(String, nullable=False)
    irrigation_preference = Column(String, nullable=False)
    plantation_type = Column(String, nullable=False)
    coconut_age = Column(String, nullable=False)
    notes = Column(Text, default="")
    status = Column(String, default="Generated")
    plan_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SmartPlanReview(Base):
    __tablename__ = "smart_plan_reviews"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("smart_plans.id"), nullable=False, unique=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, nullable=False)
    officer_note = Column(Text, default="")
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FarmLocation(Base):
    __tablename__ = "farm_locations"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    source = Column(String, default="browser-geolocation")
    created_at = Column(DateTime, default=datetime.utcnow)


class PlanVersion(Base):
    __tablename__ = "smart_plan_versions"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("smart_plans.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    change_type = Column(String, nullable=False)
    change_note = Column(Text, default="")
    layout_data = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlanChangeRequest(Base):
    __tablename__ = "plan_change_requests"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("smart_plans.id"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    change_type = Column(String, nullable=False)
    change_note = Column(Text, default="")
    status = Column(String, default="Applied")
    created_at = Column(DateTime, default=datetime.utcnow)
