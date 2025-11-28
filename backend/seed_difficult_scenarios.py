"""
Seed script to create scenarios for difficult customers.

These scenarios should produce LOW scores (3-4/10) to give evolution targets to improve.

Run: python seed_difficult_scenarios.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def seed_difficult_scenarios():
    db = SessionLocal()

    try:
        # Get Marcus
        marcus = db.query(models.Persona).filter(models.Persona.name == "Marcus").first()

        # Get difficult customers
        james = db.query(models.Persona).filter(models.Persona.name == "James (Threatening Customer)").first()
        karen = db.query(models.Persona).filter(models.Persona.name == "Karen (Dismissive Customer)").first()
        tony = db.query(models.Persona).filter(models.Persona.name == "Tony (Blame-Shifting Customer)").first()
        emma = db.query(models.Persona).filter(models.Persona.name == "Emma (Silent Customer)").first()

        if not all([marcus, james, karen, tony, emma]):
            print("[ERROR] Not all personas found. Run seed_difficult_personas.py first.")
            return

        print(f"Found Marcus (ID: {marcus.id})")
        print(f"Found difficult customers: {james.id}, {karen.id}, {tony.id}, {emma.id}")

        # Define 4 difficult scenarios (ZERO-SHOT format)
        scenarios_data = [
            {
                "name": "Customer Call - 50 Days Overdue High Risk",
                "context": "You are calling a customer about a $7,000 personal loan that is 50 days overdue. This is the first contact attempt. No prior behavioral data available. Account flagged as high risk.",
                "goal": "Secure payment commitment while de-escalating any hostility.",
                "persona_a_id": marcus.id,
                "persona_b_id": james.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 35 Days Overdue Credit Line",
                "context": "You are calling a customer about a $4,500 credit line that is 35 days overdue. First contact. Customer background unknown.",
                "goal": "Obtain specific payment date despite resistance.",
                "persona_a_id": marcus.id,
                "persona_b_id": karen.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 75 Days Overdue Business Loan",
                "context": "You are calling a customer about a $20,000 business loan that is 75 days overdue. First contact. No personality profile available.",
                "goal": "Get customer to acknowledge debt and commit to payment.",
                "persona_a_id": marcus.id,
                "persona_b_id": tony.id,
                "max_turns": 10
            },
            {
                "name": "Customer Call - 40 Days Overdue Medical Loan",
                "context": "You are calling a customer about a $6,000 medical loan that is 40 days overdue. First contact. Customer situation unknown.",
                "goal": "Engage non-responsive customer and secure commitment.",
                "persona_a_id": marcus.id,
                "persona_b_id": emma.id,
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

        print(f"\n[SUCCESS] All 4 difficult scenarios created!")
        print(f"Scenario IDs: {scenario_ids}")
        print(f"\nNow you have:")
        print(f"  - 2 original hard scenarios (IDs 1,2) scoring ~3/10")
        print(f"  - 4 NEW hard scenarios (IDs {scenario_ids}) expected ~3-4/10")
        print(f"  - 3 easy scenarios (IDs 3,4,5) scoring ~9/10")
        print(f"\nTotal: 9 scenarios (6 hard, 3 easy)")
        print(f"\nFor evolution, select scenarios: 1,2,{','.join(map(str, scenario_ids))}")
        print(f"This focuses training on difficult cases!")

        return scenario_ids

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating 4 Difficult Scenarios (Marcus vs Hard Customers)...")
    print("=" * 60)
    seed_difficult_scenarios()
    print("=" * 60)
