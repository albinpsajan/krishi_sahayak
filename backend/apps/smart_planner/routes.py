"""HTTP boundary for private plot planning and officer review workflows."""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.farmer_profile.models import User
from apps.notifications.notification_service import create_notification
from core.database import get_db
from core.security import get_current_user, require_farmer, require_officer
from .models import SmartPlot, SmartPlan, SmartPlanReview, FarmLocation, PlanVersion, PlanChangeRequest
from .schemas import PlotCreate, PlanCreate, ReviewCreate, ReviewUpdate, LocationCreate, ChangeRequest
from .services import analyse_plot, analyse_geojson, generate_plan
from services.plan_customization_service import apply_change

router = APIRouter(prefix="/api/smart-planner", tags=["smart planner"])


def plot_view(row):
    data = json.loads(row.boundary_json)
    if isinstance(data, dict):
        boundary = data.get("local_boundary", [])
        geojson = data.get("geojson")
        center_lat, center_lon = data.get("center_lat"), data.get("center_lon")
    else:
        boundary, geojson, center_lat, center_lon = data, None, None, None
    return {"id": row.id, "plot_name": row.plot_name, "village": row.village, "district": row.district,
            "boundary": boundary, "boundary_geojson": geojson, "center_lat": center_lat, "center_lon": center_lon,
            "area_sq_m": row.area_sq_m, "area_acres": row.area_acres, "area_cents": row.area_cents,
            "area_hectares": row.area_hectares, "shape_type": row.shape_type, "usable_area_sq_m": round(row.area_sq_m * .93, 1), "created_at": row.created_at}


def plan_view(row, include_json=True):
    result = json.loads(row.plan_json) if include_json else None
    return {"id": row.id, "plot_id": row.plot_id, "main_crop": row.main_crop, "water_source": row.water_source,
            "soil_type": row.soil_type, "budget_level": row.budget_level, "irrigation_preference": row.irrigation_preference,
            "plantation_type": row.plantation_type, "coconut_age": row.coconut_age, "notes": row.notes, "status": row.status,
            "created_at": row.created_at, "updated_at": row.updated_at, "plan": result}


@router.get("/rules")
def rules():
    return {"coconut": {"spacing_x_m": 7.5, "spacing_y_m": 7.5, "boundary_buffer_m": 2},
            "water_sources": ["well", "borewell", "pond", "canal", "rainfed", "other", "not sure"],
            "irrigation_methods": ["Drip irrigation", "Phased basin → drip", "Water source verification required"]}


@router.post("/plots", status_code=201)
def create_plot(payload: PlotCreate, db: Session = Depends(get_db), user: User = Depends(require_farmer)):
    try:
        analysis = analyse_geojson(payload.boundary_geojson) if payload.boundary_geojson else analyse_plot(payload.boundary)
    except ValueError as error: raise HTTPException(422, str(error))
    boundary_payload = {"local_boundary": analysis["boundary"], "geojson": analysis.get("boundary_geojson"), "center_lat": analysis.get("center_lat"), "center_lon": analysis.get("center_lon")} if analysis.get("boundary_geojson") else analysis["boundary"]
    row = SmartPlot(farmer_id=user.id, plot_name=payload.plot_name, village=payload.village, district=payload.district,
                    boundary_json=json.dumps(boundary_payload), area_sq_m=analysis["area_sq_m"], area_acres=analysis["area_acres"],
                    area_cents=analysis["area_cents"], area_hectares=analysis["area_hectares"], shape_type=analysis["shape_type"])
    db.add(row); db.commit(); db.refresh(row)
    return plot_view(row)


@router.get("/plots")
def get_plots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [plot_view(row) for row in db.query(SmartPlot).filter_by(farmer_id=user.id).order_by(SmartPlot.id.desc()).all()]


@router.get("/plots/{plot_id}")
def get_plot(plot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.get(SmartPlot, plot_id)
    if not row or (row.farmer_id != user.id and user.role not in ("OFFICER", "ADMIN")): raise HTTPException(404, "Plot not found")
    return plot_view(row)


@router.post("/plans/generate", status_code=201)
def generate(payload: PlanCreate, db: Session = Depends(get_db), user: User = Depends(require_farmer)):
    plot = db.get(SmartPlot, payload.plot_id)
    if not plot or plot.farmer_id != user.id: raise HTTPException(404, "Plot not found")
    analysis = plot_view(plot)
    analysis["created_at"] = analysis["created_at"].isoformat() if hasattr(analysis["created_at"], "isoformat") else str(analysis["created_at"])
    plan_result = generate_plan(analysis, payload.model_dump())
    row = SmartPlan(farmer_id=user.id, plot_id=plot.id, main_crop=payload.main_crop, water_source=payload.water_source,
                    soil_type=payload.soil_type, budget_level=payload.budget_level, irrigation_preference=payload.irrigation_preference,
                    plantation_type=payload.plantation_type, coconut_age=payload.coconut_age, notes=payload.notes,
                    plan_json=json.dumps(plan_result))
    db.add(row); db.commit(); db.refresh(row)
    return plan_view(row)


@router.get("/plans")
def get_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(SmartPlan)
    if user.role == "FARMER": query = query.filter_by(farmer_id=user.id)
    return [plan_view(row, include_json=False) for row in query.order_by(SmartPlan.id.desc()).all()]


@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.get(SmartPlan, plan_id)
    if not row or (row.farmer_id != user.id and user.role not in ("OFFICER", "ADMIN")): raise HTTPException(404, "Plan not found")
    return plan_view(row)


@router.post("/plans/{plan_id}/request-review")
def request_review(plan_id: int, payload: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(require_farmer)):
    row = db.get(SmartPlan, plan_id)
    if not row or row.farmer_id != user.id: raise HTTPException(404, "Plan not found")
    if row.status not in ("Generated", "Changes Requested"): raise HTTPException(409, "This plan is not ready for review.")
    review = db.query(SmartPlanReview).filter_by(plan_id=plan_id).first()
    if not review: review = SmartPlanReview(plan_id=plan_id, created_at=datetime.utcnow()); db.add(review)
    review.status, review.officer_note = "Sent for Review", payload.note
    row.status = "Sent for Review"
    create_notification(db, user_id=user.id, title="Smart Farm Plan sent for review", message="Your preliminary plantation plan is waiting for an agricultural officer.", target_link=f"/smart-planner/{plan_id}")
    db.commit(); return {"status": row.status}


@router.get("/officer/pending")
def pending(db: Session = Depends(get_db), user: User = Depends(require_officer)):
    return [plan_view(row) for row in db.query(SmartPlan).filter(SmartPlan.status.in_(["Sent for Review", "Under Review"])).order_by(SmartPlan.id.asc()).all()]


@router.patch("/plans/{plan_id}/review")
def review(plan_id: int, payload: ReviewUpdate, db: Session = Depends(get_db), user: User = Depends(require_officer)):
    row = db.get(SmartPlan, plan_id)
    if not row: raise HTTPException(404, "Plan not found")
    review_row = db.query(SmartPlanReview).filter_by(plan_id=plan_id).first()
    if not review_row: review_row = SmartPlanReview(plan_id=plan_id, created_at=datetime.utcnow()); db.add(review_row)
    review_row.officer_id, review_row.status, review_row.officer_note, review_row.reviewed_at = user.id, payload.status, payload.note, datetime.utcnow()
    row.status = payload.status
    create_notification(db, user_id=row.farmer_id, title=f"Smart Farm Plan: {payload.status}", message=payload.note or "An officer updated your plan review.", target_link=f"/smart-planner/{plan_id}")
    db.commit(); return {"status": row.status, "note": review_row.officer_note}


@router.post("/locations", status_code=201)
def save_location(payload: LocationCreate, db: Session = Depends(get_db), user: User = Depends(require_farmer)):
    row = FarmLocation(farmer_id=user.id, latitude=payload.latitude, longitude=payload.longitude, accuracy_meters=payload.accuracy_meters, source=payload.source)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "latitude": row.latitude, "longitude": row.longitude, "accuracy_meters": row.accuracy_meters, "source": row.source, "created_at": row.created_at}


@router.get("/plans/{plan_id}/versions")
def versions(plan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.get(SmartPlan, plan_id)
    if not row or (row.farmer_id != user.id and user.role not in ("OFFICER", "ADMIN")): raise HTTPException(404, "Plan not found")
    return [{"id": v.id, "version_number": v.version_number, "change_type": v.change_type, "change_note": v.change_note, "created_at": v.created_at, "layout_data": json.loads(v.layout_data)} for v in db.query(PlanVersion).filter_by(plan_id=plan_id).order_by(PlanVersion.version_number.asc()).all()]


@router.post("/plans/{plan_id}/customize", status_code=201)
def customize(plan_id: int, payload: ChangeRequest, db: Session = Depends(get_db), user: User = Depends(require_farmer)):
    row = db.get(SmartPlan, plan_id)
    if not row or row.farmer_id != user.id: raise HTTPException(404, "Plan not found")
    plot_row = db.get(SmartPlot, row.plot_id); analysis = plot_view(plot_row); analysis["created_at"] = str(analysis["created_at"])
    original = json.loads(row.plan_json); current = apply_change(row, analysis, payload.change_type, payload.change_note)
    last = db.query(PlanVersion).filter_by(plan_id=row.id).order_by(PlanVersion.version_number.desc()).first(); version_no = (last.version_number if last else 1) + 1
    if not last: db.add(PlanVersion(plan_id=row.id, version_number=1, change_type="Original generated plan", change_note="", layout_data=json.dumps(original), created_by=user.id))
    db.add(PlanVersion(plan_id=row.id, version_number=version_no, change_type=payload.change_type, change_note=payload.change_note, layout_data=json.dumps(current), created_by=user.id))
    db.add(PlanChangeRequest(plan_id=row.id, farmer_id=user.id, change_type=payload.change_type, change_note=payload.change_note, status="Applied"))
    row.plan_json = json.dumps(current); row.status = "Sent for Review" if version_no > 1 else row.status; db.commit(); db.refresh(row)
    return plan_view(row)
