from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    personality = Column(String)
    mood = Column(String)
    voice_id = Column(String)
    system_prompt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scenarios_as_a = relationship("Scenario", foreign_keys="Scenario.persona_a_id", back_populates="persona_a")
    scenarios_as_b = relationship("Scenario", foreign_keys="Scenario.persona_b_id", back_populates="persona_b")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    context = Column(String, nullable=False)
    goal = Column(String)
    persona_a_id = Column(Integer, ForeignKey("personas.id"))
    persona_b_id = Column(Integer, ForeignKey("personas.id"))
    max_turns = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    persona_a = relationship("Persona", foreign_keys=[persona_a_id], back_populates="scenarios_as_a")
    persona_b = relationship("Persona", foreign_keys=[persona_b_id], back_populates="scenarios_as_b")
    simulation_runs = relationship("SimulationRun", back_populates="scenario")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    transcript = Column(JSON)
    audio_paths = Column(JSON)
    status = Column(String, default="pending")  # pending/running/completed/failed
    duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scenario = relationship("Scenario", back_populates="simulation_runs")
    evaluation = relationship("Evaluation", back_populates="simulation_run", uselist=False)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("simulation_runs.id"))
    scores = Column(JSON)
    overall_score = Column(Float)
    feedback = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    simulation_run = relationship("SimulationRun", back_populates="evaluation")


class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"))
    version = Column(Integer)
    system_prompt = Column(String)
    fitness_score = Column(Float)
    parent_version_id = Column(Integer, ForeignKey("agent_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
