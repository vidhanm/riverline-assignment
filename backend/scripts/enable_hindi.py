"""
Enable Hindi language for all personas.

This updates all persona system prompts to conduct conversations in Hindi.
Audio will still be English (Deepgram doesn't support Hindi), but text will be Hindi.

Run: python enable_hindi.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def enable_hindi():
    db = SessionLocal()

    try:
        # Get all personas
        personas = db.query(models.Persona).all()

        print(f"Enabling Hindi for {len(personas)} personas...")
        print("=" * 80)

        for persona in personas:
            # Check if already has Hindi instruction
            if "HINDI" in persona.system_prompt.upper() or "हिंदी" in persona.system_prompt:
                print(f"[SKIP] {persona.name} - Already has Hindi instruction")
                continue

            # Prepend Hindi instruction
            old_prompt = persona.system_prompt
            new_prompt = f"IMPORTANT: Conduct the ENTIRE conversation in Hindi (Devanagari script). Use natural, colloquial Hindi appropriate for phone conversations.\n\n{old_prompt}"

            persona.system_prompt = new_prompt
            print(f"[UPDATED] {persona.name}")
            print(f"  OLD: {old_prompt[:80]}...")
            print(f"  NEW: {new_prompt[:80]}...")
            print()

        db.commit()
        print("=" * 80)
        print(f"[SUCCESS] All personas updated for Hindi conversations!")
        print("\nNote: Audio will still be in English (Deepgram limitation).")
        print("Text transcripts will be in Hindi.")

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    enable_hindi()
