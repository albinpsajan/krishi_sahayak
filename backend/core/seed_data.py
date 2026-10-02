"""
KrishiSahayak AI - Demo data seeder.

Populates demo farmer/officer accounts, subsidy schemes, a verified crop case
and initial audit records. Safe to run repeatedly: it exits early if the demo
farmer already exists.
"""

from apps.audit.audit_ledger import log_audit_action
from apps.crop_cases.models import (
    AIAssessment,
    CropCase,
    CropImage,
    OfficerReview,
    Recommendation,
)
from apps.farmer_profile.models import FarmerProfile, OfficerProfile, User
from apps.notifications.models import Notification
from apps.subsidies.models import SubsidyScheme
from core.database import Base, SessionLocal, engine, run_lightweight_migrations
from core.security import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()  # add new columns (username, age, ...) to pre-existing databases
    db = SessionLocal()

    try:
        # Backfill usernames for users created before the username field existed
        users_without_username = db.query(User).filter(User.username.is_(None)).all()
        for u in users_without_username:
            u.username = u.email.split("@")[0]  # farmer@krishi.in -> "farmer"
        if users_without_username:
            db.commit()

        existing_farmer = db.query(User).filter(User.email == "farmer@krishi.in").first()
        if existing_farmer:
            print("Database already seeded.")
            return

        print("Seeding initial KrishiSahayak AI demo data...")

        # 1. Demo Farmer
        farmer_user = User(
            email="farmer@krishi.in",
            username="farmer",
            hashed_password=hash_password("farmer123"),
            full_name="Ramanan Nair (ഡെമോ കർഷകൻ)",
            age=46,
            role="FARMER",
            phone="+91 98470 12345",
            language="ml",
            profile_completed=True,
        )
        db.add(farmer_user)
        db.flush()

        db.add(
            FarmerProfile(
                user_id=farmer_user.id,
                district="Palakkad",
                state="Kerala",
                land_size_acres=3.5,
                primary_crops="Paddy (Uma), Pepper, Coconut",
                water_source="Malampuzha Canal & Borewell",
                kissan_credit_card=True,
            )
        )

        # 2. Demo Officer
        officer_user = User(
            email="officer@krishi.in",
            username="officer",
            hashed_password=hash_password("officer123"),
            full_name="Dr. Lakshmi Priya (Senior Agri Officer)",
            age=38,
            role="OFFICER",
            phone="+91 94471 98765",
            language="en",
            profile_completed=True,
        )
        db.add(officer_user)
        db.flush()

        db.add(
            OfficerProfile(
                user_id=officer_user.id,
                officer_code="KL-AGRI-409",
                designation="Senior Agricultural Officer & Krishi Bhavan Chief",
                jurisdiction_district="Palakkad District",
                department="Department of Agriculture, Govt of Kerala",
            )
        )

        # 3. Subsidy Schemes (officer-managed source of truth)
        schemes = [
            SubsidyScheme(
                code="SCH-PADDY-01",
                name="Kerala Paddy Cultivation Incentives & Fertilizer Subsidy",
                hindi_malayalam_name="നെൽകൃഷി പ്രോത്സാഹന സഹായ പദ്ധതി",
                description="Financial support for paddy farmers providing ₹5,500/hectare subsidy for organic bio-fertilizers and pest management.",
                crop_category="Paddy",
                eligibility_criteria="Registered paddy farmers in Kerala with land area up to 5 hectares.",
                required_documents="Aadhaar Card, Land Possession Certificate (Pattayam), Bank Passbook",
                benefit_information="Direct Benefit Transfer (DBT) of ₹5,500 per hectare + free soil health testing.",
                max_subsidy_amount=15000.0,
            ),
            SubsidyScheme(
                code="SCH-SPICE-02",
                name="High-Yield Pepper & Spices Rejuvenation Scheme",
                hindi_malayalam_name="കുരുമുളക് നവീകരണ പദ്ധതി",
                description="Assistance for disease control in pepper gardens and supply of certified bio-fungicides.",
                crop_category="Pepper",
                eligibility_criteria="Farmers cultivating pepper with quick-wilt control needs.",
                required_documents="Aadhaar Card, Agri Officer Crop Health Report",
                benefit_information="100% subsidy on Trichoderma bio-agent & ₹3,000 direct spray incentive.",
                max_subsidy_amount=8000.0,
            ),
            SubsidyScheme(
                code="SCH-SOLAR-03",
                name="PM-KUSUM Off-Grid Solar Irrigation Pump Subsidy",
                hindi_malayalam_name="സൗര കൃഷി പമ്പ് പദ്ധതി (PM-KUSUM)",
                description="60% Govt subsidy for installing 3HP to 7.5HP solar water pumps for small farmers.",
                crop_category="All Crops",
                eligibility_criteria="Small & marginal landholders without active grid connection.",
                required_documents="Aadhaar Card, Land Record, Electricity NOC",
                benefit_information="60% capital cost subsidy (State 30% + Central 30%).",
                max_subsidy_amount=85000.0,
            ),
        ]
        db.add_all(schemes)
        db.flush()

        # 4. Initial seed crop case (fully verified workflow example)
        case1 = CropCase(
            case_number="CASE-2026-8801",
            farmer_id=farmer_user.id,
            crop_type="Paddy",
            variety="Uma (MO-16)",
            field_location="Chittur East Paddy Field, Block B",
            symptoms_description="Spindle-shaped diamond brown spots on upper leaf surface, slight leaf drying noticed after heavy rain.",
            status="Officer Verified",
        )
        db.add(case1)
        db.flush()

        db.add(CropImage(case_id=case1.id, image_url="assets/sample_leaf.jpg"))

        ai_ass = AIAssessment(
            case_id=case1.id,
            probable_disease="Paddy Blast (Magnaporthe oryzae)",
            hindi_malayalam_name="നെല്ലിലെ ബ്ലാസ്റ്റ് രോഗം",
            confidence=89.5,
            observations="Computer vision model detected characteristic necrotic blast lesions with chlorotic yellow borders.",
            preliminary_guidance="Spray Pseudomonas fluorescens @ 10g/L water during early morning hours.",
            malayalam_guidance="സുഡോമോണസ് ഫ്ലൂറസെൻസ് (10 ഗ്രാം/ലിറ്റർ) തളിക്കുക. നൈട്രജൻ വളം കുറയ്ക്കുക.",
        )
        db.add(ai_ass)

        off_rev = OfficerReview(
            case_id=case1.id,
            officer_id=officer_user.id,
            is_confirmed=True,
            corrected_disease=None,
            officer_notes="Field inspection confirmed early stage leaf blast. Weather conditions highly favorable for fungal spread.",
            verified_recommendation=(
                "Spray Pseudomonas fluorescens @ 10g/L immediately. Follow up with Tricyclazole 75% WP @ 0.6g/L "
                "if symptoms persist after 5 days."
            ),
            precautions="Drain standing water for 2 days. Do not apply urea fertilizer until new tillers emerge.",
            follow_up_days=5,
            malayalam_recommendation=(
                "സുഡോമോണസ് ഫ്ലൂറസെൻസ് 10 ഗ്രാം ഒരു ലിറ്റർ വെള്ളത്തിൽ കലക്കി രാവിലെ തളിക്കുക. "
                "2 ദിവസം പാടത്തെ വെള്ളം വറ്റിക്കുക."
            ),
        )
        db.add(off_rev)

        db.add(
            Recommendation(
                case_id=case1.id,
                product_name="Pseudomonas fluorescens Bio-Fungicide",
                category="Organic Bio-Agent",
                application_dosage="10g per Litre water",
                timing="Early Morning (6 AM - 8 AM)",
                guidance_notes="Procure fresh bio-agent from local Krishi Bhavan organic depot.",
            )
        )

        # 5. Initial audit records
        log_audit_action(
            db,
            actor_id=farmer_user.id,
            actor_name=farmer_user.full_name,
            actor_role="FARMER",
            action="CREATE_CROP_CASE",
            target_type="CROP_CASE",
            target_id=str(case1.id),
            metadata={"crop": "Paddy", "variety": "Uma"},
        )
        log_audit_action(
            db,
            actor_id=1,  # System AI
            actor_name="CropDoctor AI System",
            actor_role="AI_SYSTEM",
            action="GENERATE_AI_ASSESSMENT",
            target_type="AI_ASSESSMENT",
            target_id=str(ai_ass.id),
            metadata={"disease": "Paddy Blast", "confidence": 89.5},
        )
        log_audit_action(
            db,
            actor_id=officer_user.id,
            actor_name=officer_user.full_name,
            actor_role="OFFICER",
            action="VERIFY_CROP_CASE",
            target_type="OFFICER_REVIEW",
            target_id=str(off_rev.id),
            metadata={"is_confirmed": True, "action": "VERIFIED_RECOMMENDATION_ISSUED"},
        )

        # Initial notification
        db.add(
            Notification(
                user_id=farmer_user.id,
                title="✓ Officer Verified Recommendation Ready",
                message="Senior Agri Officer Dr. Lakshmi Priya has verified your Paddy Blast case #CASE-2026-8801.",
                malayalam_message="നിങ്ങളുടെ നെൽകൃഷി കേസ് കൃഷി ഓഫീസർ പരിശോധിച്ചു നിർദ്ദേശങ്ങൾ നൽകിയിട്ടുണ്ട്.",
                is_read=False,
                notification_type="success",
                target_link="/cases/1",
            )
        )

        db.commit()
        print("Demo data successfully seeded!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
