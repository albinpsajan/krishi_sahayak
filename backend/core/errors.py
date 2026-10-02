"""
Central application error codes (docs/architecture.md section 8).

Every feature raises errors through api_error() so responses always carry:
  - a stable machine-readable code (for developers/logs), and
  - a simple user-facing message (safe to show farmers/officers).
"""

from fastapi import HTTPException


class AppErrorCode:
    # Auth / profile
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    USERNAME_ALREADY_TAKEN = "USERNAME_ALREADY_TAKEN"
    INVALID_USER_DETAILS = "INVALID_USER_DETAILS"
    MISSING_FARM_PROFILE = "MISSING_FARM_PROFILE"
    ACCESS_DENIED = "ACCESS_DENIED"

    # Crop cases
    CASE_NOT_FOUND = "CASE_NOT_FOUND"
    CASE_ACCESS_DENIED = "CASE_ACCESS_DENIED"
    INVALID_CASE_DATA = "INVALID_CASE_DATA"

    # Subsidies
    SCHEME_NOT_FOUND = "SCHEME_NOT_FOUND"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    INVALID_APPLICATION_DATA = "INVALID_APPLICATION_DATA"
    SUBSIDY_MATCHING_ERROR = "SUBSIDY_MATCHING_ERROR"
    DOCUMENT_REQUIRED = "DOCUMENT_REQUIRED"

    # Infrastructure / AI
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    """Builds an HTTPException whose detail carries both the code and the message."""
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})
