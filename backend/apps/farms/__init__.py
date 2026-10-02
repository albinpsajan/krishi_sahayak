"""
Smart Irrigation Advisor feature (farms) (docs/features/irrigation.md).

Purpose
-------
Consent-based digital field records (Farm, FarmCrop) that will back the
irrigation plan engine and officer review workflow. Models are registered so
tables exist; the plan engine is a future feature and intentionally not
implemented here yet (change isolation, docs/architecture.md section 14).
"""

from apps.farms import models  # noqa: F401
