"""
Seed script to create 5 scenarios linking Marcus to each customer.

Run: python seed_scenarios.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def seed_scenarios():
    db = SessionLocal()

    try:
        # Get Marcus and customer IDs
        marcus = db.query(models.Persona).filter(models.Persona.name == "Marcus").first()
        robert = db.query(models.Persona).filter(models.Persona.name == "Robert (Angry Customer)").first()
        lisa = db.query(models.Persona).filter(models.Persona.name == "Lisa (Evasive Customer)").first()
        david = db.query(models.Persona).filter(models.Persona.name == "David (Curious Customer)").first()
        sarah = db.query(models.Persona).filter(models.Persona.name == "Sarah (Cooperative Customer)").first()
        michael = db.query(models.Persona).filter(models.Persona.name == "Michael (Desperate Customer)").first()

        if not all([marcus, robert, lisa, david, sarah, michael]):
            print("[ERROR] Not all personas found. Run seed_debt_collection.py first.")
            return

        print(f"Found Marcus (ID: {marcus.id})")
        print(f"Found 5 customers: {robert.id}, {lisa.id}, {david.id}, {sarah.id}, {michael.id}")

        # Define 5 scenarios (ZERO-SHOT: No personality hints for Marcus)
        scenarios_data = [
            {
                "name": "Customer Call - 30 Days Overdue",
                "context": "You are calling a customer about a $5,000 personal loan that is 30 days overdue. This is the first contact attempt. You have no prior information about the customer's personality or behavior.",
                "goal": "Secure a payment commitment while maintaining professionalism.",
                "persona_a_id": marcus.id,
                "persona_b_id": robert.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 60 Days Overdue",
                "context": "You are calling a customer about an $8,000 credit card debt that is 60 days overdue. This is the first contact attempt. No prior behavioral data available.",
                "goal": "Obtain specific payment date or arrangement.",
                "persona_a_id": marcus.id,
                "persona_b_id": lisa.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 45 Days Overdue Auto Loan",
                "context": "You are calling a customer about a $12,000 car loan that is 45 days overdue. First contact. Customer background unknown.",
                "goal": "Guide customer to payment plan decision.",
                "persona_a_id": marcus.id,
                "persona_b_id": david.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 20 Days Overdue Small Loan",
                "context": "You are calling a customer about a $3,000 loan that is 20 days overdue. First contact. No personality profile available.",
                "goal": "Establish concrete payment arrangement.",
                "persona_a_id": marcus.id,
                "persona_b_id": sarah.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 90 Days Overdue Large Debt",
                "context": "You are calling a customer about a $15,000 loan that is 90 days overdue. First contact. Customer situation unknown.",
                "goal": "Secure payment commitment appropriate to customer circumstances.",
                "persona_a_id": marcus.id,
                "persona_b_id": michael.id,
                "max_turns": 10
            }
        ]

        scenario_ids = []
        for scenario_data in scenarios_data:
            # Check if scenario already exists
            existing = db.query(models.Scenario).filter(models.Scenario.name == scenario_data["name"]).first()
            if existing:
                print(f"[OK] {scenario_data['name']} already exists (ID: {existing.id})")
                scenario_ids.append(existing.id)
            else:
                scenario = models.Scenario(**scenario_data)
                db.add(scenario)
                db.commit()
                db.refresh(scenario)
                scenario_ids.append(scenario.id)
                print(f"[OK] Created {scenario.name} (ID: {scenario.id})")

        print(f"\n[SUCCESS] All 5 scenarios created successfully!")
        print(f"Scenario IDs: {scenario_ids}")
        print(f"\nReady for evolution! Use these scenario IDs:")
        print(f"  POST /api/evolve/{marcus.id}?scenario_ids={','.join(map(str, scenario_ids))}")

        return scenario_ids

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating 5 Scenarios (Marcus vs Each Customer)...")
    print("=" * 60)
    seed_scenarios()
    print("=" * 60)
