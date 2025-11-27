from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("/", response_model=List[schemas.Scenario])
def list_scenarios(db: Session = Depends(get_db)):
    """List all scenarios"""
    return db.query(models.Scenario).all()


@router.post("/", response_model=schemas.Scenario)
def create_scenario(scenario: schemas.ScenarioCreate, db: Session = Depends(get_db)):
    """Create a new scenario"""
    # Verify personas exist
    persona_a = db.query(models.Persona).filter(models.Persona.id == scenario.persona_a_id).first()
    persona_b = db.query(models.Persona).filter(models.Persona.id == scenario.persona_b_id).first()

    if not persona_a or not persona_b:
        raise HTTPException(status_code=404, detail="One or both personas not found")

    db_scenario = models.Scenario(**scenario.model_dump())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


@router.get("/{scenario_id}", response_model=schemas.Scenario)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario"""
    scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.put("/{scenario_id}", response_model=schemas.Scenario)
def update_scenario(scenario_id: int, scenario_update: schemas.ScenarioUpdate, db: Session = Depends(get_db)):
    """Update a scenario"""
    scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Update only provided fields
    for key, value in scenario_update.model_dump(exclude_unset=True).items():
        setattr(scenario, key, value)

    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Delete a scenario"""
    scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    db.delete(scenario)
    db.commit()
    return {"message": "Scenario deleted"}
