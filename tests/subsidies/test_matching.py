import unittest

import tests.test_environment  # noqa: F401  (path + isolated test DB)

from apps.subsidies.services.subsidy_matcher import evaluate_subsidy_application, match_farmer_with_subsidies

FULL_DOCS = [
    {"document_type": "Aadhaar Card"},
    {"document_type": "Land Possession Certificate (Pattayam)"},
    {"document_type": "Bank Passbook"},
]


class SubsidyMatchingTests(unittest.TestCase):
    def test_eligible_farmer_gets_fast_track(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 3.5, "primary_crops": "Paddy (Uma), Pepper"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card, Land Possession Certificate"},
            application_docs=FULL_DOCS,
        )
        self.assertEqual(result["risk_level"], "LOW_RISK_FAST_TRACK")
        self.assertGreaterEqual(result["score"], 85)
        self.assertEqual(result["missing_documents"], [])
        self.assertIn("human_in_loop_notice", result)

    def test_ineligible_crop_category_flagged(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 3.5, "primary_crops": "Coconut"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card"},
            application_docs=[{"document_type": "Aadhaar Card"}],
        )
        self.assertEqual(result["risk_level"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["score"], 100 - 25)
        self.assertTrue(any("Crop category" in f for f in result["flags"]))

    def test_missing_documents_block_fast_track(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 3.5, "primary_crops": "Paddy"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card, Bank Passbook"},
            application_docs=[{"document_type": "Aadhaar Card"}],
        )
        self.assertEqual(result["risk_level"], "INCOMPLETE_DOCUMENTS")
        self.assertIn("bank passbook", result["missing_documents"])

    def test_large_landholding_requires_review(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 25.0, "primary_crops": "Paddy"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card"},
            application_docs=[{"document_type": "Aadhaar Card"}],
        )
        self.assertEqual(result["risk_level"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["score"], 100 - 15)

    def test_unverified_crop_case_reduces_score(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 3.5, "primary_crops": "Paddy"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card"},
            application_docs=[{"document_type": "Aadhaar Card"}],
            crop_case={"crop_type": "Paddy", "status": "Awaiting Officer Review"},
        )
        self.assertEqual(result["score"], 100 - 10)
        self.assertEqual(result["risk_level"], "LOW_RISK_FAST_TRACK")  # still >= 85

    def test_officer_verified_case_passes(self):
        result = evaluate_subsidy_application(
            farmer_profile={"land_size_acres": 3.5, "primary_crops": "Paddy"},
            scheme={"crop_category": "Paddy", "required_documents": "Aadhaar Card"},
            application_docs=[{"document_type": "Aadhaar Card"}],
            crop_case={"crop_type": "Paddy", "status": "Officer Verified"},
        )
        self.assertEqual(result["score"], 100)
        self.assertTrue(any("Officer-Verified" in p for p in result["rules_passed"]))

    def test_match_farmer_with_subsidies_orders_eligible_first(self):
        schemes = [
            {"id": 1, "name": "Solar Pump", "crop_category": "All Crops"},
            {"id": 2, "name": "Paddy Subsidy", "crop_category": "Paddy"},
            {"id": 3, "name": "Pepper Scheme", "crop_category": "Pepper"},
        ]
        matches = match_farmer_with_subsidies({"primary_crops": "Paddy"}, schemes)
        self.assertTrue(matches[0]["eligible"])
        self.assertEqual(matches[0]["scheme_name"], "Paddy Subsidy")
        self.assertEqual(len(matches), 3)


if __name__ == "__main__":
    unittest.main()
