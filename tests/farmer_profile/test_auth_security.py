import unittest
from datetime import timedelta

import jwt as pyjwt
import tests.test_environment  # noqa: F401

from config import settings
from core.security import create_access_token, hash_password, verify_password


class PasswordSecurityTests(unittest.TestCase):
    def test_hash_and_verify_roundtrip(self):
        hashed = hash_password("farmer123")
        self.assertNotEqual(hashed, "farmer123")
        self.assertTrue(verify_password("farmer123", hashed))
        self.assertFalse(verify_password("wrong", hashed))


class TokenTests(unittest.TestCase):
    def test_token_contains_claims_and_expiry(self):
        token = create_access_token({"sub": "farmer@krishi.in", "role": "FARMER", "id": 1})
        payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        self.assertEqual(payload["sub"], "farmer@krishi.in")
        self.assertEqual(payload["role"], "FARMER")
        self.assertIn("exp", payload)

    def test_custom_expiry_respected(self):
        token = create_access_token({"sub": "x@y.z"}, expires_delta=timedelta(hours=1))
        payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        self.assertIn("exp", payload)

    def test_token_rejected_with_wrong_secret(self):
        token = create_access_token({"sub": "x@y.z"})
        with self.assertRaises(pyjwt.InvalidSignatureError):
            pyjwt.decode(token, "not-the-secret", algorithms=[settings.JWT_ALGORITHM])


if __name__ == "__main__":
    unittest.main()
