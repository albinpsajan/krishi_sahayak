import unittest

import tests.test_environment  # noqa: F401

from apps.subsidies.services.eligibility_checker import (
    check_crop_category,
    check_land_ceiling,
    check_crop_case_verification,
)


class EligibilityRuleTests(unittest.TestCase):
    def test_crop_category_exact_match(self):
        result = check_crop_category({"primary_crops": "Paddy"}, {"crop_category": "Paddy"})
        self.assertTrue(result["passed"])

    def test_crop_category_all_crops_always_passes(self):
        result = check_crop_category({"primary_crops": "Anything"}, {"crop_category": "All Crops"})
        self.assertTrue(result["passed"])

    def test_crop_category_match_via_case(self):
        result = check_crop_category(
            {"primary_crops": "Coconut"}, {"crop_category": "Paddy"}, crop_case={"crop_type": "Paddy"}
        )
        self.assertTrue(result["passed"])

    def test_crop_category_mismatch_fails(self):
        result = check_crop_category({"primary_crops": "Coconut"}, {"crop_category": "Paddy"})
        self.assertFalse(result["passed"])

    def test_land_ceiling_small_farmer_passes(self):
        self.assertTrue(check_land_ceiling({"land_size_acres": 2.5})["passed"])

    def test_land_ceiling_boundary(self):
        self.assertTrue(check_land_ceiling({"land_size_acres": 10.0})["passed"])
        self.assertFalse(check_land_ceiling({"land_size_acres": 10.5})["passed"])

    def test_case_verification_states(self):
        self.assertTrue(check_crop_case_verification(None)["passed"])
        self.assertTrue(check_crop_case_verification({"status": "Officer Verified"})["passed"])
        self.assertFalse(check_crop_case_verification({"status": "Submitted"})["passed"])


if __name__ == "__main__":
    unittest.main()
