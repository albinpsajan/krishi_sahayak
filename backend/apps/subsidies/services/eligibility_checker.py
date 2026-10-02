"""
Eligibility checker (deterministic, docs/architecture.md section 3).

Pure functions only: no database access, no AI, no I/O. Evaluates a farmer
against a scheme's officer-managed criteria and returns a risk classification.
This module is the ONLY place that decides LOW_RISK_FAST_TRACK vs
HUMAN_REVIEW_REQUIRED vs INCOMPLETE_DOCUMENTS.
"""

# Scoring constants - tune here, tests assert against these thresholds.
BASE_SCORE = 100
CROP_MISMATCH_PENALTY = 25
LARGE_HOLDING_PENALTY = 15
MISSING_DOC_PENALTY = 35
UNVERIFIED_CASE_PENALTY = 10

SMALL_FARMER_CEILING_ACRES = 10.0
FAST_TRACK_SCORE_THRESHOLD = 85

VERIFIED_CASE_STATUSES = ("Officer Verified", "Recommendation Available")


def check_crop_category(farmer_profile: dict, scheme: dict, crop_case: dict = None) -> dict:
    """Rule 1: farmer's crops (or case crop) must match the scheme category."""
    scheme_category = scheme.get("crop_category", "All Crops").lower()
    farmer_crops = farmer_profile.get("primary_crops", "").lower()
    case_crop = crop_case.get("crop_type", "").lower() if crop_case else ""

    if scheme_category == "all crops" or scheme_category in farmer_crops or scheme_category in case_crop:
        return {"passed": True, "message": "✓ Crop category matches scheme notification criteria."}
    return {
        "passed": False,
        "message": "⚠️ Crop category discrepancy detected between scheme and farmer profile.",
    }


def check_land_ceiling(farmer_profile: dict) -> dict:
    """Rule 2: small/marginal farmer land ceiling check."""
    land_acres = farmer_profile.get("land_size_acres", 2.5)
    if land_acres <= SMALL_FARMER_CEILING_ACRES:
        return {
            "passed": True,
            "message": "✓ Farmer land holding (< 10 acres) satisfies Small/Marginal Farmer subsidy mandate.",
        }
    return {
        "passed": False,
        "message": "ℹ️ Large landholding (> 10 acres) requires manual ceiling verification by Officer.",
    }


def check_crop_case_verification(crop_case: dict = None) -> dict:
    """Rule 4: officer-verified crop diagnosis attached (when a case is linked)."""
    if not crop_case:
        return {"passed": True, "message": ""}
    if crop_case.get("status") in VERIFIED_CASE_STATUSES:
        return {"passed": True, "message": "✓ Application contains Officer-Verified crop health diagnostic proof."}
    return {"passed": False, "message": "ℹ️ Associated crop case awaiting officer diagnostic verification."}
