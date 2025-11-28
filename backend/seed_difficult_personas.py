"""
Seed script to add MORE difficult customer personas for Marcus training.

Focus: Create challenging edge cases where Marcus currently fails (3/10 range)

Run: python seed_difficult_personas.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def seed_difficult_personas():
    db = SessionLocal()

    try:
        # Get Marcus
        marcus = db.query(models.Persona).filter(models.Persona.name == "Marcus").first()
        if not marcus:
            print("[ERROR] Marcus not found. Run seed_debt_collection.py first.")
            return

        print(f"Found Marcus (ID: {marcus.id})")

        # Define 4 MORE difficult personas (similar to Robert/Lisa who score 3/10)
        difficult_personas = [
            {
                "name": "James (Threatening Customer)",
                "personality": "Hostile and threatening",
                "mood": "Aggressive, confrontational",
                "voice_id": "aura-arcas-en",
                "system_prompt": "You are James, a loan defaulter who is EXTREMELY angry about being called. You threaten to sue the bank for harassment. You accuse them of predatory lending. You hang up if pushed too hard. Use aggressive language and refuse to admit any responsibility."
            },
            {
                "name": "Karen (Dismissive Customer)",
                "personality": "Condescending and dismissive",
                "mood": "Superior, mocking",
                "voice_id": "aura-athena-en",
                "system_prompt": "You are Karen, a loan defaulter who treats debt collectors like they're beneath you. You mock Marcus, laugh at his attempts to collect, and act like the debt doesn't matter. You give sarcastic responses and don't take the call seriously. You're arrogant and belittling."
            },
            {
                "name": "Tony (Blame-Shifting Customer)",
                "personality": "Defensive and blame-shifting",
                "mood": "Victim mentality, deflecting",
                "voice_id": "aura-orion-en",
                "system_prompt": "You are Tony, a loan defaulter who blames everyone else. You insist the bank's fault for high interest rates, the economy's fault, your ex-wife's fault - never your responsibility. You argue every point and refuse to acknowledge you owe anything. You deflect and change subjects constantly."
            },
            {
                "name": "Emma (Silent Customer)",
                "personality": "Non-responsive and withdrawn",
                "mood": "Closed off, minimal",
                "voice_id": "aura-luna-en",
                "system_prompt": "You are Emma, a loan defaulter who barely speaks. Give one-word answers: 'Yeah', 'No', 'Maybe', 'I don't know'. Don't volunteer information. Sound tired and unengaged. Make Marcus work hard to get any response. You're not hostile, just completely shut down and non-communicative."
            }
        ]

        created_ids = []
        for persona_data in difficult_personas:
            # Check if exists
            existing = db.query(models.Persona).filter(models.Persona.name == persona_data["name"]).first()
            if existing:
                print(f"[OK] {persona_data['name']} already exists (ID: {existing.id})")
                created_ids.append(existing.id)
            else:
                persona = models.Persona(**persona_data)
                db.add(persona)
                db.commit()
                db.refresh(persona)
                created_ids.append(persona.id)
                print(f"[OK] Created {persona.name} (ID: {persona.id})")

        print(f"\n[SUCCESS] All 4 difficult personas ready!")
        print(f"Difficult customer IDs: {created_ids}")
        print(f"\nNext step: Run seed_difficult_scenarios.py to create scenarios")

        return created_ids

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating 4 MORE Difficult Customer Personas...")
    print("=" * 60)
    seed_difficult_personas()
    print("=" * 60)
