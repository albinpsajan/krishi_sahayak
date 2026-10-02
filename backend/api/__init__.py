"""
API layer: one router per feature (docs/architecture.md section 6).

    /api/auth/          -> auth_router      (farmer_profile feature)
    /api/profile        -> profile router   (farmer_profile feature)
    /api/upload         -> uploads router
    /api/cases/         -> cases_router     (crop_cases feature)
    /api/subsidies/     -> subsidies_router (subsidies feature)
    /api/officer/       -> officer_router   (autoclerk feature)
    /api/audit/         -> audit_router     (audit feature)
    /api/notifications/ -> notifications_router (notifications feature)
"""

from api.auth_routes import auth_router  # noqa: F401
from api.profile_routes import profile_router  # noqa: F401
from api.upload_routes import uploads_router  # noqa: F401
from api.case_routes import cases_router  # noqa: F401
from api.subsidy_routes import subsidies_router  # noqa: F401
from api.officer_routes import officer_router  # noqa: F401
from api.audit_routes import audit_router  # noqa: F401
from api.notification_routes import notifications_router  # noqa: F401
