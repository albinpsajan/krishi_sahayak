"""Auth endpoints: /api/auth/register, /api/auth/login, /api/auth/details, /api/auth/me."""

import random

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.farmer_profile.models import FarmerProfile, OfficerProfile, User
from apps.farmer_profile.schemas import (
    TokenResponse,
    UserDetailsUpdate,
    UserLogin,
    UserRegister,
    UserResponse,
)
from apps.audit.audit_ledger import log_audit_action
from core.database import get_db
from core.errors import AppErrorCode, api_error
from core.security import create_access_token, get_current_user, hash_password, verify_password

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=TokenResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Step 1 of signup: creates the account with email + username + password.
    Basic details (full name, age) and role (Farmer/Officer) are collected
    on the onboarding screen right after this, via PUT /api/auth/details.
    """
    email = payload.email.strip().lower()
    username = payload.username.strip()

    if db.query(User).filter(User.email == email).first():
        raise api_error(400, AppErrorCode.EMAIL_ALREADY_REGISTERED, "Email already registered")
    if db.query(User).filter(User.username == username).first():
        raise api_error(400, AppErrorCode.USERNAME_ALREADY_TAKEN, "Username already taken")

    # Temporary identity until the onboarding step completes
    display_name = payload.full_name.strip() or username
    if payload.role and payload.role.upper() != "FARMER":
        raise api_error(403, AppErrorCode.ACCESS_DENIED, "Staff accounts require an administrator invitation")
    role = "FARMER"

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(payload.password),
        full_name=display_name,
        role=role,
        phone=payload.phone,
        language="ml" if role == "FARMER" else "en",
        profile_completed=False,
    )
    db.add(user)
    db.flush()

    if role == "FARMER":
        db.add(FarmerProfile(user_id=user.id, district="", land_size_acres=0,
                             primary_crops="", water_source="", kissan_credit_card=False))
    else:
        db.add(OfficerProfile(user_id=user.id, officer_code=f"KL-AGRI-{random.randint(100, 999)}"))

    db.commit()
    db.refresh(user)

    log_audit_action(
        db,
        actor_id=user.id,
        actor_name=user.full_name,
        actor_role=user.role,
        action="USER_REGISTERED",
        target_type="USER",
        target_id=str(user.id),
        metadata={"role": user.role, "email": user.email, "username": user.username},
    )

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}


@auth_router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Login accepts either an email address or a username."""
    identifier = payload.identifier.strip()
    user = db.query(User).filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise api_error(401, AppErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

    if not user.hashed_password.startswith("pbkdf2_sha256$"):
        user.hashed_password = hash_password(payload.password)
        db.commit()

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}


@auth_router.put("/details", response_model=TokenResponse)
def update_user_details(
    payload: UserDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 2 of signup (onboarding): collects full name, age, and the role
    (Farmer or Officer), then completes the profile.
    """
    role = payload.role.upper()
    if role != current_user.role:
        raise api_error(403, AppErrorCode.ACCESS_DENIED, "Your account role cannot be changed here")
    if role not in ["FARMER", "OFFICER"]:
        raise api_error(400, AppErrorCode.INVALID_USER_DETAILS, "Role must be FARMER or OFFICER")
    if payload.age is not None and (payload.age < 10 or payload.age > 120):
        raise api_error(400, AppErrorCode.INVALID_USER_DETAILS, "Age must be between 10 and 120")
    if not payload.full_name.strip():
        raise api_error(400, AppErrorCode.INVALID_USER_DETAILS, "Full name is required")

    current_user.full_name = payload.full_name.strip()
    current_user.age = payload.age
    current_user.role = role
    current_user.phone = payload.phone or current_user.phone
    if payload.language in ["en", "ml"]:
        current_user.language = payload.language
    current_user.profile_completed = True

    # Create the matching profile if it does not exist yet (e.g. role changed during onboarding)
    if role == "FARMER" and not current_user.farmer_profile:
        db.add(FarmerProfile(user_id=current_user.id))
    elif role == "OFFICER" and not current_user.officer_profile:
        db.add(OfficerProfile(user_id=current_user.id, officer_code=f"KL-AGRI-{random.randint(100, 999)}"))

    db.commit()
    db.refresh(current_user)

    log_audit_action(
        db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        action="USER_PROFILE_COMPLETED",
        target_type="USER",
        target_id=str(current_user.id),
        metadata={"role": role, "age": payload.age},
    )

    token = create_access_token({"sub": current_user.email, "role": current_user.role, "id": current_user.id})
    return {"access_token": token, "token_type": "bearer", "user": current_user}


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
