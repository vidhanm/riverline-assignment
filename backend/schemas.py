from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Persona Schemas
class PersonaBase(BaseModel):
    name: str
    personality: Optional[str] = None
    mood: Optional[str] = None
    voice_id: Optional[str] = None
    system_prompt: str


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    mood: Optional[str] = None
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None


class Persona(PersonaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Scenario Schemas
class ScenarioBase(BaseModel):
    name: str
    context: str
    goal: Optional[str] = None
    persona_a_id: int
    persona_b_id: int
    max_turns: int = 10


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    context: Optional[str] = None
    goal: Optional[str] = None
    persona_a_id: Optional[int] = None
    persona_b_id: Optional[int] = None
    max_turns: Optional[int] = None


class Scenario(ScenarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Simulation Schemas
class SimulationRunBase(BaseModel):
    scenario_id: int
    transcript: Optional[List[dict]] = None
    audio_paths: Optional[List[str]] = None
    status: str = "pending"
    duration_seconds: Optional[float] = None


class SimulationRun(SimulationRunBase):
    id: int
    created_at: datetime
    evaluation: Optional["Evaluation"] = None

    class Config:
        from_attributes = True


# Evaluation Schemas
class EvaluationBase(BaseModel):
    run_id: int
    scores: dict
    overall_score: float
    feedback: Optional[str] = None


class Evaluation(EvaluationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
