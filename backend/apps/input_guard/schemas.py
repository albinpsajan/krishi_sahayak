"""Validated request contracts for farmer checks and officer reviews."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class InputCheckCreate(BaseModel):
    product_name: str = Field(min_length=2, max_length=160)
    product_type: Literal["Fertilizer", "Pesticide", "Seed", "Bio-input", "Growth promoter", "Irrigation item", "Other"]
    brand: str = Field(default="", max_length=120)
    mrp: float | None = Field(default=None, ge=0, le=100000000)
    dealer_price: float | None = Field(default=None, ge=0, le=100000000)
    quantity: float | None = Field(default=None, gt=0, le=100000000)
    quantity_unit: str = Field(default="kg", max_length=30)
    expiry_date: date | None = None
    batch_number: str = Field(default="", max_length=100)
    dealer_name: str = Field(default="", max_length=120)
    crop: str = Field(min_length=2, max_length=80)
    crop_stage: str = Field(default="", max_length=40)
    land_area: float = Field(gt=0, le=100000)
    label_crops: str = Field(default="", max_length=240)
    label_rate_per_acre: float | None = Field(default=None, gt=0, le=100000000)
    label_rate_unit: str = Field(default="kg", max_length=30)
    notes: str = Field(default="", max_length=1500)
    image_url: str = Field(default="", max_length=260)


class InputReview(BaseModel):
    decision: Literal["Approved", "Not recommended", "More details needed", "Field visit required"]
    note: str = Field(default="", max_length=2000)
