"""
KrishiSahayak AI - One-Click Application Launcher
Runs the backend FastAPI server on http://127.0.0.1:8000 and prints demo credentials.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")


def main():
    print("=" * 60)
    print("🌱 KRISHISAHAYAK AI - AGRICULTURAL ADMINISTRATION PLATFORM")
    print("=" * 60)
    print("Core Philosophy: AI handles repetitive tasks. Humans make important decisions.")
    print("-" * 60)
    print("🔑 DEMO LOGIN CREDENTIALS:")
    print("   👨‍🌾 Farmer Account : farmer@krishi.in  /  farmer123")
    print("   🏛️ Officer Account: officer@krishi.in /  officer123")
    print("-" * 60)
    print("🚀 Starting FastAPI Server on http://127.0.0.1:8000 ...")

    os.chdir(BACKEND_DIR)
    sys.path.insert(0, BACKEND_DIR)

    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
