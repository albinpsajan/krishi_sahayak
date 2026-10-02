"""
KrishiSahayak AI - Authentication & role-based authorization (JWT).

Single place for password hashing, token creation/validation and the
require_farmer / require_officer guards used by every feature router.
"""

from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from core.database import get_db
from core.errors import AppErrorCode, api_error

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def hash_password(password: str) -> str:
    return __import__("hashlib").sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = api_error(
        status.HTTP_401_UNAUTHORIZED,
        AppErrorCode.NOT_AUTHENTICATED,
        "Could not validate authentication credentials",
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    from apps.farmer_profile.models import User

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def require_farmer(current_user=Depends(get_current_user)):
    if current_user.role not in ["FARMER", "ADMIN"]:
        raise api_error(
            status.HTTP_403_FORBIDDEN,
            AppErrorCode.ACCESS_DENIED,
            "Access restricted to registered Farmers",
        )
    return current_user


def require_officer(current_user=Depends(get_current_user)):
    if current_user.role not in ["OFFICER", "ADMIN"]:
        raise api_error(
            status.HTTP_403_FORBIDDEN,
            AppErrorCode.ACCESS_DENIED,
            "Access restricted to authorized Agricultural Officers",
        )
    return current_user
