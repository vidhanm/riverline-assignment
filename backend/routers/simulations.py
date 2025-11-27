from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models
import schemas
from database import get_db
from services.llm import get_llm_response
from services.tts import text_to_speech

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.get("/", response_model=List[schemas.SimulationRun])
def list_simulations(db: Session = Depends(get_db)):
    """List all simulation runs"""
    return db.query(models.SimulationRun).order_by(models.SimulationRun.created_at.desc()).all()


@router.get("/{run_id}", response_model=schemas.SimulationRun)
def get_simulation(run_id: int, db: Session = Depends(get_db)):
    """Get a specific simulation run"""
    run = db.query(models.SimulationRun).filter(models.SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return run


@router.post("/run")
def run_simulation(scenario_id: int, db: Session = Depends(get_db)):
    """Execute a simulation from a scenario and store the result"""
    # Get scenario with personas
    scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create simulation run record
    simulation_run = models.SimulationRun(
        scenario_id=scenario_id,
        status="running"
    )
    db.add(simulation_run)
    db.commit()
    db.refresh(simulation_run)

    try:
        start_time = datetime.utcnow()

        # Get personas
        persona_a = scenario.persona_a
        persona_b = scenario.persona_b

        print(f"\n=== Starting Simulation: {scenario.name} ===")
        print(f"Persona A: {persona_a.name}")
        print(f"Persona B: {persona_b.name}")
        print(f"Max turns: {scenario.max_turns}\n")

        # Run conversation with concise responses
        transcript = []
        messages_a = [{"role": "user", "content": scenario.context}]
        messages_b = []

        # Conciseness instruction for natural dialogue
        concise_instruction = """IMPORTANT: Keep responses SHORT and NATURAL (1-3 sentences max).
Speak directly as your character without stage directions, labels, or parenthetical notes.
Act like a real conversation, not a script."""

        for turn in range(scenario.max_turns):
            # Agent A speaks
            print(f"Turn {turn + 1}: Agent A ({persona_a.name}) generating response...")
            enhanced_prompt_a = f"{concise_instruction}\n\n{persona_a.system_prompt}"
            response_a = get_llm_response(enhanced_prompt_a, messages_a, max_tokens=150)
            print(f"Turn {turn + 1}: Agent A ({persona_a.name}) response complete")
            audio_a = text_to_speech(response_a, persona_a.voice_id)
            if audio_a:
                print(f"Turn {turn + 1}: Agent A ({persona_a.name}) audio generated")

            transcript.append({
                "agent": "A",
                "persona": persona_a.name,
                "text": response_a,
                "audio": audio_a
            })
            messages_a.append({"role": "assistant", "content": response_a})
            messages_b.append({"role": "user", "content": response_a})

            # Agent B responds
            print(f"Turn {turn + 1}: Agent B ({persona_b.name}) generating response...")
            enhanced_prompt_b = f"{concise_instruction}\n\n{persona_b.system_prompt}"
            response_b = get_llm_response(enhanced_prompt_b, messages_b, max_tokens=150)
            print(f"Turn {turn + 1}: Agent B ({persona_b.name}) response complete")
            audio_b = text_to_speech(response_b, persona_b.voice_id)
            if audio_b:
                print(f"Turn {turn + 1}: Agent B ({persona_b.name}) audio generated")

            transcript.append({
                "agent": "B",
                "persona": persona_b.name,
                "text": response_b,
                "audio": audio_b
            })
            messages_b.append({"role": "assistant", "content": response_b})
            messages_a.append({"role": "user", "content": response_b})

        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print(f"\n=== Simulation Complete ===")
        print(f"Duration: {duration:.2f}s")
        print(f"Total turns: {len(transcript)} messages\n")

        # Update simulation run
        simulation_run.transcript = transcript
        simulation_run.status = "completed"
        simulation_run.duration_seconds = duration
        db.commit()
        db.refresh(simulation_run)

        return simulation_run

    except Exception as e:
        # Mark as failed
        simulation_run.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.delete("/{run_id}")
def delete_simulation(run_id: int, db: Session = Depends(get_db)):
    """Delete a simulation run"""
    run = db.query(models.SimulationRun).filter(models.SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")

    db.delete(run)
    db.commit()
    return {"message": "Simulation run deleted"}
