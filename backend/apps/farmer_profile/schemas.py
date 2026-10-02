"""Pydantic schemas for auth & profile endpoints."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    """Step 1 signup: email + username + password. Basic details collected after login."""
    email: str = Field(max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    username: str = Field(min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)
    full_name: str = ""
    role: str = ""  # optional here; selected during onboarding if omitted
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Login accepts either an email address or a username."""
    identifier: str  # email OR username
    password: str


class UserDetailsUpdate(BaseModel):
    """Step 2 onboarding: basic details + role selection (farmer or officer)."""
    full_name: str
    age: int
    role: str  # FARMER or OFFICER
    phone: Optional[str] = None
    language: Optional[str] = None  # 'en' or 'ml'


class UserResponse(BaseModel):
    id: int
    email: str
    username: str = ""
    full_name: str
    role: str
    age: Optional[int] = None
    phone: Optional[str] = None
    language: str = "en"
    profile_completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
