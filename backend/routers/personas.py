from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/personas", tags=["personas"])


@router.get("/", response_model=List[schemas.Persona])
def list_personas(db: Session = Depends(get_db)):
    """List all personas"""
    return db.query(models.Persona).all()


@router.post("/", response_model=schemas.Persona)
def create_persona(persona: schemas.PersonaCreate, db: Session = Depends(get_db)):
    """Create a new persona"""
    db_persona = models.Persona(**persona.model_dump())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona


@router.get("/{persona_id}", response_model=schemas.Persona)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    """Get a specific persona"""
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.put("/{persona_id}", response_model=schemas.Persona)
def update_persona(persona_id: int, persona_update: schemas.PersonaUpdate, db: Session = Depends(get_db)):
    """Update a persona"""
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Update only provided fields
    for key, value in persona_update.model_dump(exclude_unset=True).items():
        setattr(persona, key, value)

    db.commit()
    db.refresh(persona)
    return persona


@router.delete("/{persona_id}")
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a persona"""
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    db.delete(persona)
    db.commit()
    return {"message": "Persona deleted"}
