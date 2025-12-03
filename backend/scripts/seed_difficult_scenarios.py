"""
Seed script to create scenarios for difficult customers and CHAMELEON customers.

Difficult scenarios: Produce LOW scores (3-4/10) to give evolution targets to improve.
Chameleon scenarios: Test ADAPTATION - customers that change behavior mid-conversation.

Run: python seed_difficult_scenarios.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        
        # Get chameleon customers (NEW)
        alex = db.query(models.Persona).filter(models.Persona.name == "Alex (Chameleon - Hostile to Cooperative)").first()
        maya = db.query(models.Persona).filter(models.Persona.name == "Maya (Chameleon - Evasive to Desperate)").first()
        chris = db.query(models.Persona).filter(models.Persona.name == "Chris (Chameleon - Random Mood Swings)").first()
        priya = db.query(models.Persona).filter(models.Persona.name == "Priya (Chameleon - Disputor to Settler)").first()

        if not all([marcus, james, karen, tony, emma]):
            print("[ERROR] Not all difficult personas found. Run seed_difficult_personas.py first.")
            return

        print(f"Found Marcus (ID: {marcus.id})")
        print(f"Found difficult customers: {james.id}, {karen.id}, {tony.id}, {emma.id}")
        
        # Check for chameleon personas
        chameleons_available = all([alex, maya, chris, priya])
        if chameleons_available:
            print(f"Found chameleon customers: {alex.id}, {maya.id}, {chris.id}, {priya.id}")
        else:
            print("[WARNING] Chameleon personas not found. Run seed_difficult_personas.py again to create them.")

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
        
        # Add chameleon scenarios if personas exist (NEW)
        if chameleons_available:
            chameleon_scenarios = [
                {
                    "name": "ADAPTIVE TEST - Hostile to Cooperative",
                    "context": "You are calling a customer about an $8,000 loan that is 55 days overdue. First contact. Customer behavior UNKNOWN - they may change during conversation.",
                    "goal": "Detect hostility, de-escalate effectively, and convert to cooperative resolution. Success measured by ADAPTATION quality.",
                    "persona_a_id": marcus.id,
                    "persona_b_id": alex.id,
                    "max_turns": 12
                },
                {
                    "name": "ADAPTIVE TEST - Evasive to Desperate",
                    "context": "You are calling a customer about a $12,000 loan that is 70 days overdue. First contact. Customer may not reveal true situation immediately.",
                    "goal": "Uncover the real situation behind evasive behavior through empathetic questioning. Success measured by ability to get to root cause.",
                    "persona_a_id": marcus.id,
                    "persona_b_id": maya.id,
                    "max_turns": 12
                },
                {
                    "name": "ADAPTIVE TEST - Volatile Mood Swings",
                    "context": "You are calling a customer about a $6,000 loan that is 45 days overdue. Customer has anxiety/mood challenges. Their behavior may shift unpredictably.",
                    "goal": "Handle emotional volatility with patience and consistent professionalism. Success measured by maintaining rapport despite mood changes.",
                    "persona_a_id": marcus.id,
                    "persona_b_id": chris.id,
                    "max_turns": 12
                },
                {
                    "name": "ADAPTIVE TEST - Dispute to Settlement",
                    "context": "You are calling a customer about a $10,000 loan that is 60 days overdue. Customer may dispute the debt initially.",
                    "goal": "Handle dispute professionally without getting defensive, then convert to payment arrangement. Success measured by dispute resolution skills.",
                    "persona_a_id": marcus.id,
                    "persona_b_id": priya.id,
                    "max_turns": 12
                }
            ]
            scenarios_data.extend(chameleon_scenarios)

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

        print(f"\n[SUCCESS] All scenarios created!")
        print(f"Scenario IDs: {scenario_ids}")
        print(f"\nScenario Types:")
        print(f"  - 4 Difficult static personas (test raw handling)")
        if chameleons_available:
            print(f"  - 4 Chameleon adaptive personas (test ADAPTATION)")
        print(f"\nFor COMPREHENSIVE evolution, include chameleon scenarios!")
        print(f"This trains Marcus to DETECT and ADAPT to changing behavior.")

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
