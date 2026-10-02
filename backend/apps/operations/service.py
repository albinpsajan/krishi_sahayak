"""Workflow rules. Changes and their activity records commit together."""
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from .models import Activity, Booking, Resource


def record(db, user, kind, target_id, message):
    db.add(Activity(actor_id=user.id, target_type=kind, target_id=target_id, message=message))


def transition_booking(db, user, booking, status):
    is_staff = user.role in ("OFFICER", "ADMIN")
    if not is_staff and booking.farmer_id != user.id:
        raise HTTPException(403, "This request belongs to another farmer.")
    allowed = {"Requested": {"Confirmed", "Cancelled"}, "Confirmed": {"Completed", "Cancelled"}}
    if status not in allowed.get(booking.status, set()):
        raise HTTPException(409, "This request cannot move to that status.")
    if not is_staff and status != "Cancelled":
        raise HTTPException(403, "Only the coordinator can confirm or complete a request.")
    booking.status = status
    booking.reservation_key = f"{booking.resource_id}:{booking.date}:{booking.slot}" if status == "Confirmed" else None
    record(db, user, "booking", booking.id, f"Request {status.lower()}")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This equipment is already reserved for that slot. Choose another slot.")
    return booking


def booking_view(db, row):
    resource = db.get(Resource, row.resource_id)
    return {"id": row.id, "farmer_id": row.farmer_id, "resource_id": row.resource_id,
            "resource_name": resource.name, "provider": resource.provider,
            "date": row.date, "slot": row.slot, "notes": row.notes, "status": row.status}
