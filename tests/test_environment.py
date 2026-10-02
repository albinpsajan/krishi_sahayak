"""
Shared test bootstrap.

Puts the backend package on sys.path and, crucially, points KRISHI_DB_PATH at
an empty temporary file BEFORE any backend module is imported, so tests never
read or write the developer's real demo database.
"""

import os
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Isolated per-process database (set before importing backend modules)
os.environ["KRISHI_DB_PATH"] = os.path.join(tempfile.gettempdir(), f"krishi_test_{os.getpid()}.db")
