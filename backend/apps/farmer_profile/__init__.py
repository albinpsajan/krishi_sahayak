"""
Farmer Digital Profile feature (docs/features/farmer-profile.md).

Purpose
-------
Owns the User account, FarmerProfile and OfficerProfile tables. This is the
single source of truth for identity and farm data; every other feature
(subsidies, crop cases, autoclerk) reads farmer information through
profile_service instead of duplicating it (docs/architecture.md sections 5 & 13).
"""

from apps.farmer_profile import models, schemas, profile_service  # noqa: F401
