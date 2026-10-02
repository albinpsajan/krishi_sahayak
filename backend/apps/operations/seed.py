"""Explicitly illustrative local data, attached only to the seeded demo account."""
from datetime import date, timedelta
from apps.farmer_profile.models import User
from apps.farms.models import Farm, FarmCrop
from core.database import SessionLocal
from .models import Resource, Cooperation, Participant, CashEntry


def seed_operations():
    with SessionLocal() as db:
        farmer = db.query(User).filter_by(username="farmer").first()
        if not farmer:
            return
        if not db.query(Resource).first():
            db.add_all([
                Resource(name="Tractor & cultivator", category="Machinery", provider="Palakkad Farm Collective", location="Palakkad", rate=850, unit="hour", description="45 HP tractor with an operator. Fuel included; final duration agreed before confirmation."),
                Resource(name="Harvest transport", category="Transport", provider="Green Route Logistics", location="Palakkad", rate=1800, unit="trip", description="Small goods carrier. Confirm load, route and handling charges with the coordinator."),
                Resource(name="Portable water pump", category="Irrigation", provider="Village Equipment Bank", location="Palakkad", rate=450, unit="day", description="Diesel pump with delivery hose. Fuel and transport quoted separately."),
                Resource(name="Harvesting team", category="Labour", provider="Local Farm Services", location="Palakkad", rate=750, unit="person / day", description="Request the number of workers in your notes. Availability requires confirmation."),
            ])
        if not db.query(Farm).filter_by(farmer_id=farmer.id).first():
            for name, crop, area, days, stage in [("Canal-side field", "Paddy", 2, 52, "vegetative"), ("Garden plot", "Banana", 1, 115, "flowering"), ("Homestead", "Coconut", .5, 300, "fruiting")]:
                farm = Farm(farmer_id=farmer.id, name=name, area_acres=area, water_source="Canal", soil_type="Loamy")
                db.add(farm)
                db.flush()
                db.add(FarmCrop(farm_id=farm.id, crop_name=crop, variety="Local variety", growth_stage=stage, planting_date=str(date.today()-timedelta(days=days))))
        if not db.query(Cooperation).first():
            group = Cooperation(title="A shared ride to the market", category="Transport", location="Palakkad", date=str(date.today()+timedelta(days=7)), description="Combine compatible harvest loads into one pickup. Route, quantities and cost shares will be agreed before anyone commits.", owner_id=farmer.id)
            db.add(group)
            db.flush()
            db.add(Participant(case_id=group.id, farmer_id=farmer.id))
        if not db.query(CashEntry).filter_by(farmer_id=farmer.id).first():
            for crop, cat, kind, amount in [("Paddy", "Seed", "Expense", 3200), ("Paddy", "Labour", "Expense", 4500), ("Banana", "Transport", "Expense", 1800), ("Coconut", "Harvest sale", "Income", 14600)]:
                db.add(CashEntry(farmer_id=farmer.id, crop=crop, category=cat, kind=kind, amount=amount, date=str(date.today()), note="Illustrative demo entry"))
        db.commit()
