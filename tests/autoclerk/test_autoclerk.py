import unittest

import tests.test_environment  # noqa: F401

from apps.autoclerk.autoclerk_service import generate_autoclerk_report


class AutoClerkReportTests(unittest.TestCase):
    def test_report_contains_core_sections(self):
        report = generate_autoclerk_report(
            crop_case={
                "case_number": "CASE-2026-8801",
                "crop_type": "Paddy",
                "field_location": "Chittur",
                "symptoms_description": "Spots",
            },
            farmer={"full_name": "Ramanan Nair", "phone": "+91 98470 12345", "district": "Palakkad"},
            ai_assessment={"probable_disease": "Paddy Blast", "confidence": 89.5, "observations": "Eye spots"},
            officer_review={"is_confirmed": True, "verified_recommendation": "Spray Pseudomonas"},
        )
        self.assertIn("OFFICIAL AGRICULTURAL INCIDENT & DIAGNOSTIC REPORT", report["content_markdown"])
        self.assertIn("Ramanan Nair", report["content_markdown"])
        self.assertIn("Paddy Blast", report["content_markdown"])
        self.assertEqual(report["case_number"], "CASE-2026-8801")
        self.assertFalse(report["is_finalized"])

    def test_pending_review_when_no_officer_decision(self):
        report = generate_autoclerk_report(
            crop_case={"case_number": "CASE-1", "crop_type": "Tomato", "field_location": "X", "symptoms_description": "Y"},
            farmer={"full_name": "F", "phone": "P"},
            ai_assessment={"probable_disease": "Blight", "confidence": 90, "observations": "O"},
            officer_review=None,
        )
        self.assertIn("Pending Review", report["content_markdown"])

    def test_subsidy_summary_included_when_present(self):
        report = generate_autoclerk_report(
            crop_case={"case_number": "CASE-2", "crop_type": "Paddy", "field_location": "X", "symptoms_description": "Y"},
            farmer={"full_name": "F", "phone": "P"},
            ai_assessment=None,
            officer_review=None,
            subsidy_app={"scheme_name": "Paddy Scheme", "status": "Rule Screening", "risk_level": "LOW_RISK_FAST_TRACK"},
        )
        self.assertIn("Paddy Scheme", report["content_markdown"])


if __name__ == "__main__":
    unittest.main()
