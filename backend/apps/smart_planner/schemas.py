from datetime import date
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class PlotCreate(BaseModel):
    plot_name: str = Field(min_length=2, max_length=100)
    village: str = Field(default="", max_length=100)
    district: str = Field(default="", max_length=100)
    # `boundary` is retained for backwards compatibility with saved local sketches.
    boundary: Optional[List[List[float]]] = Field(default=None, min_length=3, max_length=100)
    boundary_geojson: Optional[Dict[str, Any]] = None
    center_lat: Optional[float] = Field(default=None, ge=-90, le=90)
    center_lon: Optional[float] = Field(default=None, ge=-180, le=180)


class PlanCreate(BaseModel):
    plot_id: int
    main_crop: Literal["Coconut"] = "Coconut"
    water_source: Literal["well", "borewell", "pond", "canal", "rainfed", "other", "not sure"]
    soil_type: Literal["sandy", "laterite", "clay", "loamy", "not sure"]
    budget_level: Literal["low", "medium", "high"]
    irrigation_preference: Literal["low-cost", "water-saving", "long-term", "not sure"]
    plantation_type: Literal["new", "existing"] = "new"
    coconut_age: Literal["new", "1–3 years", "4–7 years", "mature"] = "new"
    notes: str = Field(default="", max_length=2000)


class ReviewCreate(BaseModel):
    note: str = Field(default="", max_length=2000)


class ReviewUpdate(BaseModel):
    status: Literal["Approved", "Changes Requested", "Rejected", "Field Verification Required"]
    note: str = Field(default="", max_length=2000)


class LocationCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(default=None, ge=0, le=100000)
    source: str = Field(default="browser-geolocation", max_length=60)


class ChangeRequest(BaseModel):
    change_type: Literal["Change irrigation method", "Move water source", "Change crop spacing", "Add/remove intercrop", "Reduce cost", "Add walking path", "Custom change"]
    change_note: str = Field(default="", max_length=2000)
