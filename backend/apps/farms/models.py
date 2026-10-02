"""
Farm & irrigation models: Farm, FarmCrop, IrrigationPlan, IrrigationComponent,
IrrigationOfficerReview.

Location data is stored minimally (boundary polygon + centroid) and used only
for field-specific recommendations, per the consent model.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class Farm(Base):
    """Consent-based digital field record owned by a farmer."""

    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, default="My Farm")
    boundary_json = Column(Text, nullable=True)  # JSON: [[lat, lng], ...]
    area_sqm = Column(Float, default=0.0)
    area_acres = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True)  # sandy, loamy, clay, laterite, unknown
    water_source = Column(String, nullable=True)  # well, borewell, pond, canal, rainwater, other
    water_availability = Column(String, nullable=True)  # adequate, seasonal, limited, unknown
    has_pump = Column(Boolean, default=False)
    has_storage_tank = Column(Boolean, default=False)
    existing_irrigation = Column(String, default="none")  # none, flood, sprinkler, drip
    electricity_available = Column(Boolean, default=True)
    location_permission = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="farms")
    crop_records = relationship("FarmCrop", back_populates="farm", cascade="all, delete-orphan")
    irrigation_plans = relationship("IrrigationPlan", back_populates="farm", cascade="all, delete-orphan")


class FarmCrop(Base):
    """Crop planted on a farm for an irrigation advisory cycle."""

    __tablename__ = "farm_crops"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    crop_name = Column(String, nullable=False)  # Tomato, Banana, Coconut, Paddy, Vegetable
    variety = Column(String, nullable=True)
    growth_stage = Column(String, default="vegetative")  # initial, vegetative, flowering, fruiting, maturity
    planting_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="crop_records")
    irrigation_plans = relationship("IrrigationPlan", back_populates="crop", cascade="all, delete-orphan")


class IrrigationPlan(Base):
    """
    Engine + AI generated irrigation recommendation.
    Status flow: DRAFT -> AI_GENERATED -> SUBMITTED_FOR_REVIEW -> UNDER_REVIEW
                 -> APPROVED | CHANGES_REQUESTED | REJECTED
    """

    __tablename__ = "irrigation_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_number = Column(String, unique=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("farm_crops.id"), nullable=False)

    recommended_method = Column(String, default="drip")  # drip, sprinkler, surface
    confidence = Column(Float, default=0.0)  # 0-100, never 100
    water_requirement_lpd = Column(Float, default=0.0)  # litres per day (whole field)
    per_plant_lpd = Column(Float, nullable=True)  # litres per plant per day (drip crops)
    irrigation_frequency_days = Column(Float, default=1.0)
    session_duration_min = Column(Float, default=30.0)
    sessions_per_day = Column(Float, default=1.0)
    num_zones = Column(Integer, default=1)
    lateral_spacing_m = Column(Float, nullable=True)
    pipe_length_m = Column(Float, default=0.0)
    emitters_count = Column(Integer, default=0)
    sprinklers_count = Column(Integer, default=0)
    daily_rainfall_mm = Column(Float, default=0.0)  # forecast captured at generation time
    effective_rainfall_mm = Column(Float, default=0.0)

    cost_min = Column(Float, default=0.0)
    cost_max = Column(Float, default=0.0)
    cost_options_json = Column(Text, nullable=True)  # JSON: [{tier, label, total_min, total_max, features}]
    schedule_json = Column(Text, nullable=True)  # JSON: 7-day schedule with weather adjustments
    layout_json = Column(Text, nullable=True)  # JSON: water source, mainline, submain, laterals, emitters
    weather_json = Column(Text, nullable=True)  # JSON: forecast snapshot used by the engine
    reasoning = Column(Text, nullable=True)  # farmer-friendly AI explanation
    reasoning_ml = Column(Text, nullable=True)  # Malayalam explanation
    confidence_breakdown_json = Column(Text, nullable=True)  # JSON: high/medium/needs-verification factors
    safety_notice = Column(Text, nullable=True)

    status = Column(String, default="AI_GENERATED")
    officer_comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="irrigation_plans")
    crop = relationship("FarmCrop", back_populates="irrigation_plans")
    components = relationship("IrrigationComponent", back_populates="plan", cascade="all, delete-orphan")
    officer_reviews = relationship("IrrigationOfficerReview", back_populates="plan", cascade="all, delete-orphan")


class IrrigationComponent(Base):
    """Bill of quantities line item for an irrigation plan cost estimate."""

    __tablename__ = "irrigation_components"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("irrigation_plans.id"), nullable=False, index=True)
    component_type = Column(String, nullable=False)  # mainline_pipe, lateral_pipe, emitter, sprinkler, filter, pump...
    specification = Column(String, nullable=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="nos")  # nos, metre, unit
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    plan = relationship("IrrigationPlan", back_populates="components")


class IrrigationOfficerReview(Base):
    """Human-in-the-loop officer verification for an irrigation plan."""

    __tablename__ = "irrigation_officer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("irrigation_plans.id"), nullable=False, index=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String, nullable=False)  # APPROVED, MODIFIED, CHANGES_REQUESTED, REJECTED
    comments = Column(Text, nullable=True)
    modified_parameters = Column(Text, nullable=True)  # JSON of officer-overridden engine parameters
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("IrrigationPlan", back_populates="officer_reviews")
    officer = relationship("User")
