"""Pydantic schemas for subsidy endpoints."""

from typing import Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class SubsidySchemeResponse(BaseModel):
    id: int
    code: str
    name: str
    hindi_malayalam_name: Optional[str] = None
    description: str
    crop_category: str
    eligibility_criteria: str
    required_documents: str
    benefit_information: str
    max_subsidy_amount: float

    class Config:
        from_attributes = True


class SubsidyApplicationCreate(BaseModel):
    scheme_id: int
    crop_case_id: Optional[int] = None
    requested_subsidy_amount: float = Field(default=5000.0, gt=0, le=10000000)


class SubsidyDecision(BaseModel):
    status: Literal["Approved", "Rejected", "Info Requested"]
    approved_amount: Optional[float] = Field(default=None, ge=0)
    decision_notes: str = Field(max_length=2000)


class SubsidyApplicationResponse(BaseModel):
    id: int
    application_number: str
    farmer_id: int
    farmer_name: Optional[str] = None
    scheme_id: int
    scheme_name: Optional[str] = None
    crop_case_id: Optional[int] = None
    status: str
    risk_level: str
    rule_engine_output: Optional[str] = None
    requested_subsidy_amount: float
    approved_subsidy_amount: Optional[float] = None
    officer_decision_notes: Optional[str] = None
    applied_at: datetime

    class Config:
        from_attributes = True
