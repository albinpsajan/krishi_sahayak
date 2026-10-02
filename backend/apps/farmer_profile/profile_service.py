"""
Profile service (docs/architecture.md section 5 & 13).

Other features must fetch farmer/officer information through these functions
rather than querying User/FarmerProfile tables directly, so profile data has
exactly one source of truth:

    Farmer Profile -> profile_service -> Subsidies / Crop Cases / AutoClerk
"""

from apps.farmer_profile.models import FarmerProfile, OfficerProfile


def get_farmer_profile(db, user_id: int) -> FarmerProfile:
    """Returns the FarmerProfile row for a user, or None."""
    return db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()


def get_farmer_context(db, user) -> dict:
    """
    Returns the minimal farmer facts other features need (subsidy rules,
    AutoClerk reports). Centralised so the shape changes in one place only.
    """
    fp = get_farmer_profile(db, user.id)
    return {
        "full_name": user.full_name,
        "phone": user.phone,
        "district": fp.district if fp else "Palakkad",
        "state": fp.state if fp else "Kerala",
        "land_size_acres": fp.land_size_acres if fp else 2.5,
        "primary_crops": fp.primary_crops if fp else "Paddy",
    }


def get_officer_profile(db, user_id: int) -> OfficerProfile:
    """Returns the OfficerProfile row for a user, or None."""
    return db.query(OfficerProfile).filter(OfficerProfile.user_id == user_id).first()


def build_profile_response(user) -> dict:
    """Builds the /api/profile payload (account facts + role-specific profile)."""
    res = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone": user.phone,
        "language": user.language,
    }
    if user.role == "FARMER" and user.farmer_profile:
        fp = user.farmer_profile
        res["farmer_profile"] = {
            "district": fp.district,
            "state": fp.state,
            "land_size_acres": fp.land_size_acres,
            "primary_crops": fp.primary_crops,
            "water_source": fp.water_source,
            "kissan_credit_card": fp.kissan_credit_card,
        }
    elif user.role == "OFFICER" and user.officer_profile:
        op = user.officer_profile
        res["officer_profile"] = {
            "officer_code": op.officer_code,
            "designation": op.designation,
            "jurisdiction_district": op.jurisdiction_district,
            "department": op.department,
        }
    return res
