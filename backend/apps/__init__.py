"""
Feature packages live here (docs/architecture.md section 1):
farmer_profile, crop_cases, subsidies, audit, notifications, autoclerk, farms.

Importing this package imports every feature's models so SQLAlchemy can
resolve string-based relationships across features and create all tables.
"""

from apps import farmer_profile  # noqa: F401
from apps import crop_cases  # noqa: F401
from apps import subsidies  # noqa: F401
from apps import audit  # noqa: F401
from apps import notifications  # noqa: F401
from apps import autoclerk  # noqa: F401
from apps import farms  # noqa: F401
from apps import operations  # noqa: F401
from apps import community  # noqa: F401
from apps import smart_planner  # noqa: F401
