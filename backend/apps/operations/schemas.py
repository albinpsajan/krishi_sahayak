"""Validated input contracts shared by operations routes."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class PlotInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    crop: str = Field(min_length=2, max_length=60)
    variety: str = Field(default="Local variety", max_length=100)
    area: float = Field(gt=0, le=100000)
    water_source: str = Field(min_length=2, max_length=100)
    planting_date: date
    growth_stage: Literal["initial", "vegetative", "flowering", "fruiting", "maturity"] = "vegetative"


class BookingInput(BaseModel):
    resource_id: int
    date: date
    slot: Literal["Morning", "Afternoon"]
    notes: str = Field(default="", max_length=1000)
    request_key: str = Field(min_length=10, max_length=100)


class StatusInput(BaseModel):
    status: str = Field(max_length=60)


class GroupInput(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    category: Literal["Group selling", "Shared machinery", "Group buying", "Transport"]
    location: str = Field(min_length=2, max_length=100)
    date: date
    description: str = Field(min_length=10, max_length=1500)


class CashInput(BaseModel):
    crop: str = Field(min_length=2, max_length=80)
    category: str = Field(min_length=2, max_length=80)
    kind: Literal["Expense", "Income"]
    amount: float = Field(gt=0, le=100000000)
    date: date
    note: str = Field(default="", max_length=500)


class ProfileInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(max_length=25)
    district: str = Field(min_length=2, max_length=100)
    water_source: str = Field(min_length=2, max_length=100)
