"""
Seed script to create Marcus (debt collector) + 5 customer personas
for Riverline assignment multi-scenario evolution testing.

Run: python seed_debt_collection.py
"""

import sys
import os

# Add parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

def seed_personas():
    db = SessionLocal()

    try:
        # Check if Marcus already exists
        existing_marcus = db.query(models.Persona).filter(models.Persona.name == "Marcus").first()
        if existing_marcus:
            print("[OK] Marcus already exists")
            marcus_id = existing_marcus.id
        else:
            # Create Marcus (Debt Collector)
            marcus = models.Persona(
                name="Marcus",
                personality="Debt collector",
                mood="Professional",
                voice_id="aura-asteria-en",
                system_prompt="You are Marcus, a debt collector calling about overdue loan payments. Try to get the customer to make a payment."
            )
            db.add(marcus)
            db.commit()
            db.refresh(marcus)
            marcus_id = marcus.id
            print(f"[OK] Created Marcus (ID: {marcus_id})")

        # Customer personas
        customers = [
            {
                "name": "Robert (Angry Customer)",
                "personality": "Hostile, defensive, threatens legal action",
                "mood": "Angry, frustrated",
                "voice_id": "aura-angus-en",
                "system_prompt": "You are Robert, a loan defaulter who is angry about being called. You feel harassed and defensive. Respond with hostility, threaten legal action, refuse to cooperate. Interrupt frequently."
            },
            {
                "name": "Lisa (Evasive Customer)",
                "personality": "Avoids commitment, makes excuses",
                "mood": "Evasive, non-committal",
                "voice_id": "aura-luna-en",
                "system_prompt": "You are Lisa, a loan defaulter who avoids direct answers. Make excuses about why you can't pay. Promise to call back later. Dodge questions about payment dates. Never commit to anything specific."
            },
            {
                "name": "David (Curious Customer)",
                "personality": "Asks many questions, wants options",
                "mood": "Inquisitive, careful",
                "voice_id": "aura-orpheus-en",
                "system_prompt": "You are David, a loan defaulter who wants to understand all options. Ask detailed questions about payment plans, interest rates, penalties, and consequences. Want to make informed decisions."
            },
            {
                "name": "Sarah (Cooperative Customer)",
                "personality": "Willing to pay, needs guidance",
                "mood": "Cooperative, apologetic",
                "voice_id": "aura-luna-en",
                "system_prompt": "You are Sarah, a loan defaulter who wants to pay but needs help. Be apologetic about missing payments. Ask about payment plan options. Show willingness to resolve the debt. Respond positively to solutions."
            },
            {
                "name": "Michael (Desperate Customer)",
                "personality": "Emotional, financial hardship",
                "mood": "Desperate, emotional",
                "voice_id": "aura-angus-en",
                "system_prompt": "You are Michael, a loan defaulter facing severe financial hardship. Express emotional distress about job loss, medical bills, or family crisis. Plead for understanding and extensions. Show genuine desperation."
            }
        ]

        customer_ids = []
        for customer_data in customers:
            # Check if customer already exists
            existing = db.query(models.Persona).filter(models.Persona.name == customer_data["name"]).first()
            if existing:
                print(f"[OK] {customer_data['name']} already exists")
                customer_ids.append(existing.id)
            else:
                customer = models.Persona(**customer_data)
                db.add(customer)
                db.commit()
                db.refresh(customer)
                customer_ids.append(customer.id)
                print(f"[OK] Created {customer.name} (ID: {customer.id})")

        print(f"\n[SUCCESS] All 6 personas created successfully!")
        print(f"Marcus ID: {marcus_id}")
        print(f"Customer IDs: {customer_ids}")

        return marcus_id, customer_ids

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating Marcus + 5 Customer Personas...")
    print("=" * 60)
    seed_personas()
    print("=" * 60)
    print("\nNext step: Run seed_scenarios.py to create 5 scenarios")
