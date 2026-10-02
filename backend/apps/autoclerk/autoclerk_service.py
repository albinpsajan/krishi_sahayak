"""
AutoClerk official report engine.

Synthesizes a structured administrative report for the Agricultural Officer.
Every value is taken from the inputs (case, farmer, AI assessment, officer
review, subsidy application); this module only formats.
"""

from datetime import datetime


def generate_autoclerk_report(
    crop_case: dict, farmer: dict, ai_assessment: dict, officer_review: dict = None, subsidy_app: dict = None
) -> dict:
    """Builds the AutoClerk markdown report from the supplied facts."""
    case_num = crop_case.get("case_number", "CASE-1001")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    farmer_name = farmer.get("full_name", "N/A")
    farmer_phone = farmer.get("phone", "N/A")
    district = farmer.get("district", "Palakkad")

    crop = crop_case.get("crop_type", "N/A")
    location = crop_case.get("field_location", "N/A")
    symptoms = crop_case.get("symptoms_description", "N/A")

    ai_disease = ai_assessment.get("probable_disease", "N/A") if ai_assessment else "Not Processed"
    ai_conf = f"{ai_assessment.get('confidence', 0)}%" if ai_assessment else "N/A"
    ai_obs = ai_assessment.get("observations", "N/A") if ai_assessment else "N/A"

    if officer_review:
        is_conf = "Confirmed" if officer_review.get("is_confirmed") else "Corrected"
        final_diag = officer_review.get("corrected_disease") or ai_disease
        off_notes = officer_review.get("officer_notes", "None")
        off_rec = officer_review.get("verified_recommendation", "N/A")
    else:
        is_conf = "Pending Review"
        final_diag = "Pending Verification"
        off_notes = "Awaiting Officer Field Review"
        off_rec = "Awaiting Officer Recommendation"

    subsidy_summary = "No associated subsidy application"
    if subsidy_app:
        scheme_name = subsidy_app.get("scheme_name", "Govt Scheme")
        sub_status = subsidy_app.get("status", "Submitted")
        risk = subsidy_app.get("risk_level", "HUMAN_REVIEW_REQUIRED")
        subsidy_summary = f"Scheme: {scheme_name} | Status: {sub_status} | Screening Risk: {risk}"

    report_markdown = f"""# OFFICIAL AGRICULTURAL INCIDENT & DIAGNOSTIC REPORT
**Report Reference:** AUTOCLERK-{case_num}  
**Date of Generation:** {now_str}  
**Department:** Department of Agriculture & Farmers Welfare, Govt of Kerala / India  

---

## 1. APPLICANT & LAND DETAILS
- **Farmer Name:** {farmer_name}
- **Contact Number:** {farmer_phone}
- **Jurisdiction District:** {district}
- **Field Parcel Location:** {location}

## 2. CROP CASE & DIAGNOSTIC SUMMARY
- **Case Reference:** {case_num}
- **Target Crop:** {crop}
- **Reported Field Symptoms:** {symptoms}

## 3. PRELIMINARY AI DIAGNOSIS (CropDoctor System)
- **AI Probable Issue:** {ai_disease}
- **Confidence Rating:** {ai_conf}
- **Computer Vision Observations:** {ai_obs}
- *Disclaimer: AI assessment generated automatically for preliminary decision support.*

## 4. OFFICER FIELD VERIFICATION & FINDINGS
- **Verification Status:** {is_conf}
- **Officer Final Diagnostic:** {final_diag}
- **Officer Inspection Notes:** {off_notes}
- **Mandated Recommendation & Treatment Plan:** {off_rec}

## 5. SUBSIDY & ASSISTANCE STATUS
- **Subsidy Match Summary:** {subsidy_summary}

---
**Verification Seal & Officer Approval:**  
*Pending Final Sign-off by Authorized Senior Agricultural Officer.*
"""

    return {
        "report_id": f"REP-{case_num}",
        "case_number": case_num,
        "title": f"AutoClerk Verification Report - {case_num} ({crop})",
        "generated_at": now_str,
        "content_markdown": report_markdown,
        "is_finalized": False,
    }
