"""
Subsidy matcher (deterministic, docs/architecture.md section 3).

Orchestrates the eligibility and document rules into a single screening
result used for risk classification. NEVER auto-approves or auto-rejects:
the Agricultural Officer holds sole decision authority. No AI in this file.
"""

import logging

from apps.subsidies.services.eligibility_checker import (
    BASE_SCORE,
    CROP_MISMATCH_PENALTY,
    LARGE_HOLDING_PENALTY,
    MISSING_DOC_PENALTY,
    UNVERIFIED_CASE_PENALTY,
    FAST_TRACK_SCORE_THRESHOLD,
    check_crop_category,
    check_land_ceiling,
    check_crop_case_verification,
)
from apps.subsidies.services.document_checker import find_missing_documents

logger = logging.getLogger("krishi.subsidies")

HUMAN_IN_LOOP_NOTICE = (
    "CRITICAL MANDATE: This automated screening serves purely as decision support. "
    "The Agricultural Officer holds sole authority to Approve or Reject."
)


def match_farmer_with_subsidies(farmer_profile: dict, schemes: list) -> list:
    """
    Returns the schemes a farmer could apply to (crop category matches),
    ordered best-first. Explanation only - amounts always come from the
    scheme record, never from this function.
    """
    matches = []
    for scheme in schemes:
        crop_check = check_crop_category(farmer_profile, scheme)
        matches.append(
            {
                "scheme_id": scheme.get("id"),
                "scheme_name": scheme.get("name"),
                "eligible": crop_check["passed"],
                "match_reason": crop_check["message"],
            }
        )
    matches.sort(key=lambda m: (not m["eligible"], m["scheme_name"] or ""))
    return matches


def evaluate_subsidy_application(
    farmer_profile: dict, scheme: dict, application_docs: list, crop_case: dict = None
) -> dict:
    """
    Evaluates a subsidy application against eligibility criteria, land size
    thresholds and document requirements; produces a risk classification.
    """
    rules_passed = []
    flags = []
    score = BASE_SCORE
    land_needs_manual_verification = False

    # Rule 1: crop category match
    crop_check = check_crop_category(farmer_profile, scheme, crop_case)
    if crop_check["passed"]:
        rules_passed.append(crop_check["message"])
    else:
        flags.append(crop_check["message"])
        score -= CROP_MISMATCH_PENALTY

    # Rule 2: land size threshold (a large holding always needs officer ceiling verification)
    land_check = check_land_ceiling(farmer_profile)
    if land_check["passed"]:
        rules_passed.append(land_check["message"])
    else:
        flags.append(land_check["message"])
        score -= LARGE_HOLDING_PENALTY
        land_needs_manual_verification = True

    # Rule 3: required document completeness (delegated to document_checker)
    missing_docs = find_missing_documents(scheme, application_docs)
    if not missing_docs:
        rules_passed.append("✓ All mandatory verification documents uploaded and attached.")
    else:
        flags.append(f"⚠️ Missing required documents: {', '.join(missing_docs)}")
        score -= MISSING_DOC_PENALTY

    # Rule 4: officer-verified crop diagnosis (when a case is linked)
    case_check = check_crop_case_verification(crop_case)
    if case_check["passed"]:
        if case_check["message"]:
            rules_passed.append(case_check["message"])
    else:
        flags.append(case_check["message"])
        score -= UNVERIFIED_CASE_PENALTY

    # Risk classification. Missing documents take precedence; a large landholding
    # can never fast-track because the ceiling flag mandates manual verification.
    if missing_docs:
        risk_level = "INCOMPLETE_DOCUMENTS"
        recommendation = (
            "DOCUMENT REQUEST REQUIRED: Applicant missing mandatory verification files. "
            "Recommend requesting additional documents."
        )
    elif land_needs_manual_verification:
        risk_level = "HUMAN_REVIEW_REQUIRED"
        recommendation = (
            "STANDARD HUMAN REVIEW REQUIRED: Large landholding requires manual ceiling "
            "verification by the Agricultural Officer."
        )
    elif score >= FAST_TRACK_SCORE_THRESHOLD:
        risk_level = "LOW_RISK_FAST_TRACK"
        recommendation = (
            "RECOMMEND FAST-TRACK APPROVAL: Applicant meets all documented criteria with "
            "high confidence. Prepared for Officer sign-off."
        )
    else:
        risk_level = "HUMAN_REVIEW_REQUIRED"
        recommendation = (
            "STANDARD HUMAN REVIEW REQUIRED: Special parameters or document nuances "
            "detected requiring Officer verification."
        )

    result = {
        "score": max(score, 0),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "rules_passed": rules_passed,
        "flags": flags,
        "missing_documents": missing_docs,
        "human_in_loop_notice": HUMAN_IN_LOOP_NOTICE,
    }

    logger.info(
        "[SUBSIDY_MATCH] score=%s risk=%s rules_passed=%s flags=%s missing_docs=%s",
        result["score"],
        risk_level,
        len(rules_passed),
        len(flags),
        len(missing_docs),
    )
    return result
