"""Authenticated operations HTTP boundary; workflow rules live in services."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from apps.farms.models import Farm, FarmCrop
from apps.operations.models import Resource, Booking, Cooperation, Participant, CashEntry, DocumentCheck, Activity
from apps.operations.schemas import PlotInput, BookingInput, StatusInput, GroupInput, CashInput, ProfileInput
from apps.operations.service import record, transition_booking, booking_view
from core.database import get_db
from core.security import get_current_user, require_farmer, require_officer

router = APIRouter(prefix="/api/operations", tags=["farm operations"])


@router.get("/plots")
def plots(db=Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Farm).filter_by(farmer_id=user.id).all()
    return [{"id": p.id, "name": p.name, "area": p.area_acres, "water_source": p.water_source,
             "crop": p.crop_records[-1].crop_name if p.crop_records else "Not planted",
             "planting_date": p.crop_records[-1].planting_date if p.crop_records else None,
             "growth_stage": p.crop_records[-1].growth_stage if p.crop_records else "initial"} for p in rows]


@router.post("/plots", status_code=201)
def add_plot(payload: PlotInput, db=Depends(get_db), user=Depends(require_farmer)):
    if payload.planting_date > date.today():
        raise HTTPException(422, "Planting date cannot be in the future.")
    farm = Farm(farmer_id=user.id, name=payload.name, area_acres=payload.area, water_source=payload.water_source)
    db.add(farm)
    db.flush()
    db.add(FarmCrop(farm_id=farm.id, crop_name=payload.crop, variety=payload.variety, planting_date=str(payload.planting_date), growth_stage=payload.growth_stage))
    record(db, user, "plot", farm.id, "Plot and crop season created")
    db.commit()
    return {"id": farm.id}


@router.put("/profile")
def update_profile(payload: ProfileInput, db=Depends(get_db), user=Depends(require_farmer)):
    user.full_name, user.phone = payload.full_name, payload.phone
    user.farmer_profile.district = payload.district
    user.farmer_profile.water_source = payload.water_source
    db.commit()
    return {"saved": True}


@router.get("/resources")
def resources(db=Depends(get_db), user=Depends(get_current_user)):
    return db.query(Resource).all()


@router.get("/bookings")
def bookings(db=Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Booking)
    if user.role == "FARMER":
        q = q.filter_by(farmer_id=user.id)
    return [booking_view(db, r) for r in q.order_by(Booking.id.desc()).all()]


@router.post("/bookings", status_code=201)
def book(payload: BookingInput, db=Depends(get_db), user=Depends(require_farmer)):
    if payload.date < date.today():
        raise HTTPException(422, "Choose today or a future date.")
    if not db.get(Resource, payload.resource_id):
        raise HTTPException(404, "Resource not found")
    existing = db.query(Booking).filter_by(request_key=payload.request_key).first()
    if existing:
        if existing.farmer_id != user.id:
            raise HTTPException(409, "Request key already used")
        return booking_view(db, existing)
    values = payload.model_dump()
    values["date"] = str(payload.date)
    row = Booking(**values, farmer_id=user.id)
    db.add(row)
    try:
        db.flush()
        record(db, user, "booking", row.id, "Farmer requested a slot; confirmation pending")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Request already received. Refresh your requests.")
    return booking_view(db, row)


@router.patch("/bookings/{booking_id}")
def booking_status(booking_id: int, payload: StatusInput, db=Depends(get_db), user=Depends(get_current_user)):
    row = db.get(Booking, booking_id)
    if not row:
        raise HTTPException(404, "Request not found")
    return booking_view(db, transition_booking(db, user, row, payload.status))


@router.get("/groups")
def groups(db=Depends(get_db), user=Depends(get_current_user)):
    result = []
    for row in db.query(Cooperation).order_by(Cooperation.id.desc()).all():
        members = db.query(Participant).filter_by(case_id=row.id).all()
        result.append({"id": row.id, "title": row.title, "category": row.category, "location": row.location,
                       "date": row.date, "description": row.description, "status": row.status,
                       "count": len(members), "joined": any(m.farmer_id == user.id for m in members),
                       "history": [{"message": a.message, "created_at": a.created_at} for a in db.query(Activity).filter_by(target_type="group", target_id=row.id).order_by(Activity.id).all()]})
    return result


@router.post("/groups", status_code=201)
def add_group(payload: GroupInput, db=Depends(get_db), user=Depends(require_farmer)):
    if payload.date < date.today():
        raise HTTPException(422, "Choose a future coordination date.")
    values = payload.model_dump()
    values["date"] = str(payload.date)
    row = Cooperation(**values, owner_id=user.id)
    db.add(row)
    db.flush()
    db.add(Participant(case_id=row.id, farmer_id=user.id))
    record(db, user, "group", row.id, "Group opened; organiser joined")
    db.commit()
    return {"id": row.id}


@router.post("/groups/{group_id}/join")
def join_group(group_id: int, db=Depends(get_db), user=Depends(require_farmer)):
    group = db.get(Cooperation, group_id)
    if not group:
        raise HTTPException(404, "Group not found")
    if group.status != "Gathering interest" or group.date < str(date.today()):
        raise HTTPException(409, "This group is no longer accepting participants.")
    if not db.query(Participant).filter_by(case_id=group_id, farmer_id=user.id).first():
        db.add(Participant(case_id=group_id, farmer_id=user.id))
        record(db, user, "group", group_id, "A farmer joined the group")
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    return {"joined": True}


@router.patch("/groups/{group_id}")
def advance_group(group_id: int, payload: StatusInput, db=Depends(get_db), user=Depends(require_officer)):
    row = db.get(Cooperation, group_id)
    if not row:
        raise HTTPException(404, "Group not found")
    stages = ["Gathering interest", "Coordinating", "Scheduled", "Completed"]
    if row.status == stages[-1] or payload.status != stages[stages.index(row.status)+1]:
        raise HTTPException(409, "Complete the current stage first.")
    row.status = payload.status
    record(db, user, "group", row.id, f"Coordinator moved the group to {row.status.lower()}")
    db.commit()
    return {"status": row.status}


@router.get("/cashbook")
def cashbook(db=Depends(get_db), user=Depends(get_current_user)):
    return db.query(CashEntry).filter_by(farmer_id=user.id).order_by(CashEntry.date.desc(), CashEntry.id.desc()).all()


@router.post("/cashbook", status_code=201)
def add_cash(payload: CashInput, db=Depends(get_db), user=Depends(require_farmer)):
    values = payload.model_dump()
    values["date"] = str(payload.date)
    row = CashEntry(**values, farmer_id=user.id)
    db.add(row)
    db.commit()
    return {"id": row.id}


@router.get("/documents")
def documents(db=Depends(get_db), user=Depends(get_current_user)):
    return [r.name for r in db.query(DocumentCheck).filter_by(farmer_id=user.id).all()]


@router.put("/documents/{name}")
def toggle_document(name: str, db=Depends(get_db), user=Depends(require_farmer)):
    if name not in ["Identity proof", "Land record", "Bank details", "Crop insurance", "Application receipt"]:
        raise HTTPException(422, "Unknown document type")
    row = db.query(DocumentCheck).filter_by(farmer_id=user.id, name=name).first()
    if row:
        db.delete(row)
    else:
        db.add(DocumentCheck(farmer_id=user.id, name=name))
    db.commit()
    return {"saved": True}
