"""
Central configuration for KrishiSahayak AI.

Reads every tunable value from environment variables (see .env.example) with
safe local-development fallbacks. No secrets belong in this file.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # backend/config
BACKEND_DIR = os.path.dirname(BASE_DIR)                 # backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)             # repository root

# --- Database ---
_db_path = os.environ.get("KRISHI_DB_PATH") or os.path.join(BACKEND_DIR, "krishi_sahayak.db")
DB_PATH = _db_path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# --- Security ---
# NOTE: the fallback secret keeps the local demo working; production MUST set
# JWT_SECRET_KEY in the environment (docs/architecture.md section 7).
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "krishi_sahayak_jwt_secret_hackathon_2026_super_secure"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# --- Static files & uploads ---
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "assets")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DIST_ASSETS_DIR = os.path.join(DIST_DIR, "assets")

# --- AI provider (optional external vision service) ---
CROP_DOCTOR_API_KEY = os.environ.get("CROP_DOCTOR_API_KEY") or ""

# --- CORS ---
CORS_ORIGINS = [o.strip() for o in (os.environ.get("CORS_ORIGINS") or "*").split(",")]


def ensure_directories():
    """Create runtime directories that may not exist on a fresh checkout."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
