import unittest

import tests.test_environment  # noqa: F401

from ai.crop_doctor import crop_doctor_ai


class CropDoctorAITests(unittest.TestCase):
    def test_known_crop_returns_full_contract(self):
        result = crop_doctor_ai.analyze_crop_image(
            crop_type="Paddy", image_filename="assets/sample_leaf.jpg", symptoms="Leaf drying"
        )
        for key in (
            "probable_disease", "hindi_malayalam_name", "confidence",
            "observations", "preliminary_guidance", "malayalam_guidance", "raw_ai_response",
        ):
            self.assertIn(key, result)
        self.assertIn("Paddy Blast", result["probable_disease"])

    def test_confidence_stays_bounded(self):
        for crop in ("Tomato", "Pepper", "Cotton", "Wheat"):
            result = crop_doctor_ai.analyze_crop_image(crop_type=crop, image_filename="x.jpg")
            self.assertGreaterEqual(result["confidence"], 80.0)
            self.assertLessEqual(result["confidence"], 95.0)

    def test_unknown_crop_falls_back_to_paddy(self):
        result = crop_doctor_ai.analyze_crop_image(crop_type="Dragonfruit", image_filename="x.jpg")
        self.assertIn("probable_disease", result)

    def test_symptoms_appended_to_observations(self):
        result = crop_doctor_ai.analyze_crop_image(
            crop_type="Tomato", image_filename="x.jpg", symptoms="Curling leaves"
        )
        self.assertIn("Curling leaves", result["observations"])

    def test_malayalam_translation_helper(self):
        out = crop_doctor_ai.generate_malayalam_translation("Spray neem oil")
        self.assertIn("Spray neem oil", out)


if __name__ == "__main__":
    unittest.main()
