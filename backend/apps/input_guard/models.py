"""Persisted product checks and their officer decision."""
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text

from core.database import Base


class InputCheck(Base):
    __tablename__ = "input_guard_checks"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    farmer_name = Column(String(120), default="")
    product_name = Column(String(160), nullable=False)
    product_type = Column(String(40), nullable=False)
    brand = Column(String(120), default="")
    mrp = Column(Float, nullable=True)
    dealer_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    quantity_unit = Column(String(30), default="kg")
    expiry_date = Column(Date, nullable=True)
    batch_number = Column(String(100), default="")
    dealer_name = Column(String(120), default="")
    crop = Column(String(80), nullable=False)
    crop_stage = Column(String(40), default="")
    land_area = Column(Float, nullable=False)
    label_crops = Column(String(240), default="")
    label_rate_per_acre = Column(Float, nullable=True)
    label_rate_unit = Column(String(30), default="kg")
    notes = Column(Text, default="")
    image_url = Column(String(260), default="")
    status = Column(String(40), default="Submitted", nullable=False, index=True)
    suitability_status = Column(String(40), nullable=False)
    suitability_reason = Column(Text, nullable=False)
    weather_status = Column(String(40), nullable=False)
    weather_note = Column(Text, nullable=False)
    weather_source = Column(String(50), default="")
    weather_location = Column(String(120), default="")
    rain_chance = Column(Integer, nullable=True)
    wind_kmh = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    price_status = Column(String(40), nullable=False)
    price_note = Column(Text, nullable=False)
    estimated_quantity = Column(Float, nullable=True)
    estimated_unit = Column(String(30), default="")
    quantity_note = Column(Text, nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    officer_name = Column(String(120), default="")
    officer_note = Column(Text, default="")
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
