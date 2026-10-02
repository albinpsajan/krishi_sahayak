"""
KrishiSahayak AI - FastAPI application entrypoint.

Deliberately thin: it only wires configuration, static mounts and the
per-feature routers. All endpoint logic lives in backend/api/*_routes.py and
feature services in backend/apps/*.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import apps  # noqa: F401  (registers every feature's models with SQLAlchemy)
from api import (
    audit_router,
    auth_router,
    cases_router,
    notifications_router,
    officer_router,
    profile_router,
    subsidies_router,
    uploads_router,
)
from config import settings
from core.database import Base, engine, run_lightweight_migrations
from core.logging_config import configure_logging
from core.seed_data import seed_database
from api.operation_routes import router as operations_router
from apps.operations.seed import seed_operations
from api.community_routes import router as community_router
from apps.smart_planner.routes import router as smart_planner_router
from api.live_data_routes import router as live_data_router

# Create tables, add new columns to existing DBs, then seed demo data
Base.metadata.create_all(bind=engine)
run_lightweight_migrations()
seed_database()
seed_operations()

app = FastAPI(
    title="KrishiSahayak AI API",
    description="AI-powered agricultural administration platform connecting farmers and agricultural officers.",
    version="1.1.0",
)

configure_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static asset directories (uploads + built frontend)
settings.ensure_directories()

if os.path.isdir(settings.UPLOADS_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

if os.path.isdir(settings.DIST_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=settings.DIST_ASSETS_DIR), name="assets")
elif os.path.isdir(settings.UPLOADS_DIR):
    app.mount("/assets", StaticFiles(directory=settings.UPLOADS_DIR), name="assets")


@app.get("/", include_in_schema=False)
def read_root():
    index_path = os.path.join(settings.DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "KrishiSahayak AI API Server Running", "docs": "/docs"}


# Feature-separated routers (docs/architecture.md section 6)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(uploads_router)
app.include_router(cases_router)
app.include_router(subsidies_router)
app.include_router(officer_router)
app.include_router(audit_router)
app.include_router(notifications_router)
app.include_router(operations_router)
app.include_router(community_router)
app.include_router(smart_planner_router)
app.include_router(live_data_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
