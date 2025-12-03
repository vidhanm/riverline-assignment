"""
Master seed script - runs all seed scripts in correct order.

This initializes the database with:
1. Marcus (debt collector) + 5 basic customer personas
2. 5 basic scenarios
3. 4 difficult + 4 chameleon personas
4. 8 difficult/adaptive scenarios

Run: python scripts/seed_all.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed_debt_collection import seed_personas
from scripts.seed_scenarios import seed_scenarios
from scripts.seed_difficult_personas import seed_difficult_personas
from scripts.seed_difficult_scenarios import seed_difficult_scenarios


def seed_all():
    """Run all seed scripts in order"""
    print("=" * 60)
    print("SEEDING DATABASE - Full Setup")
    print("=" * 60)
    
    print("\n[1/4] Creating Marcus + 5 basic customer personas...")
    print("-" * 40)
    seed_personas()
    
    print("\n[2/4] Creating 5 basic scenarios...")
    print("-" * 40)
    seed_scenarios()
    
    print("\n[3/4] Creating difficult + chameleon personas...")
    print("-" * 40)
    seed_difficult_personas()
    
    print("\n[4/4] Creating difficult + adaptive scenarios...")
    print("-" * 40)
    seed_difficult_scenarios()
    
    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETE!")
    print("=" * 60)
    print("\nYou now have:")
    print("  - 1 debt collector (Marcus) with adaptive prompts")
    print("  - 9 customer personas (5 basic + 4 difficult)")
    print("  - 4 chameleon personas (behavior changes mid-conversation)")
    print("  - 13 scenarios total")
    print("\nReady for evolution testing!")


if __name__ == "__main__":
    seed_all()
