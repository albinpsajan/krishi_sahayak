"""Pydantic schemas for crop case endpoints."""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class CropCaseCreate(BaseModel):
    crop_type: str = Field(min_length=2, max_length=80)
    variety: Optional[str] = None
    field_location: str = Field(min_length=2, max_length=200)
    symptoms_description: str = Field(min_length=10, max_length=3000)
    image_base64_or_url: Optional[str] = None


class AIAssessmentResponse(BaseModel):
    id: int
    probable_disease: str
    hindi_malayalam_name: Optional[str] = None
    confidence: float
    observations: str
    preliminary_guidance: str
    malayalam_guidance: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OfficerReviewCreate(BaseModel):
    is_confirmed: bool = True
    corrected_disease: Optional[str] = None
    officer_notes: Optional[str] = None
    verified_recommendation: str = Field(min_length=10, max_length=5000)
    precautions: Optional[str] = None
    follow_up_days: int = Field(default=7, ge=1, le=90)
    malayalam_recommendation: Optional[str] = None
    recommended_product: Optional[str] = None
    product_category: Optional[str] = "Organic Fungicide"
    product_dosage: Optional[str] = "5ml / Litre"


class OfficerReviewResponse(BaseModel):
    id: int
    officer_id: int
    is_confirmed: bool
    corrected_disease: Optional[str]
    officer_notes: Optional[str]
    verified_recommendation: str
    precautions: Optional[str]
    follow_up_days: int
    malayalam_recommendation: Optional[str]
    reviewed_at: datetime

    class Config:
        from_attributes = True


class CropCaseResponse(BaseModel):
    id: int
    case_number: str
    farmer_id: int
    farmer_name: Optional[str] = None
    crop_type: str
    variety: Optional[str]
    field_location: str
    symptoms_description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    images: List[str] = []
    ai_assessment: Optional[AIAssessmentResponse] = None
    officer_review: Optional[OfficerReviewResponse] = None

    class Config:
        from_attributes = True
