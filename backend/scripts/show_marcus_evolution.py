"""
Show Marcus's evolution history across all versions.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def show_evolution():
    db = SessionLocal()

    try:
        # Get all Marcus versions
        versions = db.query(models.AgentVersion).filter(
            models.AgentVersion.persona_id == 1
        ).order_by(models.AgentVersion.version).all()

        print(f"\nMarcus Evolution History ({len(versions)} versions)")
        print("=" * 100)

        for v in versions:
            print(f"\n{'[ACTIVE]' if v.is_active else '[ARCHIVED]'} VERSION {v.version} (ID: {v.id})")
            print(f"Fitness Score: {v.fitness_score}/10")
            print(f"Parent Version: {v.parent_version_id if v.parent_version_id else 'Original'}")
            print(f"Created: {v.created_at}")
            print(f"\nSystem Prompt:")
            print(f'"{v.system_prompt}"')
            print("-" * 100)

        # Show current Marcus prompt (from personas table)
        marcus = db.query(models.Persona).filter(models.Persona.id == 1).first()
        print(f"\n\nCURRENT ACTIVE PROMPT (in personas table):")
        print("=" * 100)
        print(f'"{marcus.system_prompt}"')
        print("=" * 100)

    finally:
        db.close()

if __name__ == "__main__":
    show_evolution()
