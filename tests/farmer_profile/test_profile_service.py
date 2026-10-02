import unittest

import tests.test_environment  # noqa: F401

from apps.farmer_profile.models import FarmerProfile, OfficerProfile, User
from apps.farmer_profile.profile_service import build_profile_response, get_farmer_context, get_farmer_profile
from core.database import Base, SessionLocal, engine


class ProfileServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        cls.farmer = User(
            email="profile-test@krishi.in",
            username="profiletest",
            hashed_password="x",
            full_name="Profile Tester",
            role="FARMER",
            phone="+91 90000 00000",
        )
        cls.db.add(cls.farmer)
        cls.db.flush()
        cls.db.add(
            FarmerProfile(
                user_id=cls.farmer.id,
                district="Palakkad",
                land_size_acres=4.2,
                primary_crops="Paddy, Pepper",
            )
        )
        cls.officer = User(
            email="profile-officer@krishi.in",
            username="profileofficer",
            hashed_password="x",
            full_name="Officer Tester",
            role="OFFICER",
        )
        cls.db.add(cls.officer)
        cls.db.flush()
        cls.db.add(OfficerProfile(user_id=cls.officer.id, officer_code="KL-TEST-001"))
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_get_farmer_profile_returns_row(self):
        fp = get_farmer_profile(self.db, self.farmer.id)
        self.assertIsNotNone(fp)
        self.assertEqual(fp.land_size_acres, 4.2)

    def test_farmer_context_shape(self):
        ctx = get_farmer_context(self.db, self.farmer)
        self.assertEqual(ctx["full_name"], "Profile Tester")
        self.assertEqual(ctx["land_size_acres"], 4.2)
        self.assertIn("Paddy", ctx["primary_crops"])

    def test_profile_response_farmer_block(self):
        res = build_profile_response(self.farmer)
        self.assertEqual(res["role"], "FARMER")
        self.assertIn("farmer_profile", res)
        self.assertNotIn("officer_profile", res)

    def test_profile_response_officer_block(self):
        self.db.refresh(self.officer)
        res = build_profile_response(self.officer)
        self.assertEqual(res["role"], "OFFICER")
        self.assertIn("officer_profile", res)
        self.assertEqual(res["officer_profile"]["officer_code"], "KL-TEST-001")


if __name__ == "__main__":
    unittest.main()
