from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from services.llm import get_llm_response
from services.tts import text_to_speech
from database import engine
import models
from routers import personas, scenarios, simulations, search, evolve

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voice AI Sandbox")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    persona_a_prompt: str
    persona_b_prompt: str
    context: str
    max_turns: int = 10


# Serve static files
BASE_DIR = Path(__file__).parent
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(personas.router)
app.include_router(scenarios.router)
app.include_router(simulations.router)
app.include_router(search.router)
app.include_router(evolve.router)


@app.get("/")
def root():
    return {"message": "Voice AI Sandbox API"}


@app.post("/api/simulate")
def simulate(request: SimulateRequest):
    """Run conversation between two AI personas"""
    transcript = []

    # Initialize Agent A with context to start conversation
    messages_a = [{"role": "user", "content": request.context}]
    messages_b = []

    for turn in range(request.max_turns):
        # Agent A speaks
        response_a = get_llm_response(request.persona_a_prompt, messages_a)

        # Generate audio for Agent A
        audio_a = text_to_speech(response_a)

        transcript.append({
            "agent": "A",
            "text": response_a,
            "audio": audio_a  # May be None if TTS failed
        })
        messages_a.append({"role": "assistant", "content": response_a})
        messages_b.append({"role": "user", "content": response_a})

        # Agent B responds
        response_b = get_llm_response(request.persona_b_prompt, messages_b)

        # Generate audio for Agent B
        audio_b = text_to_speech(response_b)

        transcript.append({
            "agent": "B",
            "text": response_b,
            "audio": audio_b  # May be None if TTS failed
        })
        messages_b.append({"role": "assistant", "content": response_b})
        messages_a.append({"role": "user", "content": response_b})

    return {"transcript": transcript}
