## PROJECT_PLAN.md

```markdown
# Voice AI Sandbox Platform - Implementation Plan

## Overview
Build a voice AI simulation platform where two AI personas can have conversations, generate audio, store logs, evaluate performance, and eventually self-improve via DGM (Darwin Gödel Machine).

---

## Tech Stack

- Frontend: React + Vite + Tailwind
- Backend: FastAPI (Python)
- Database: SQLite + SQLAlchemy
- Vector DB: ChromaDB (local)
- LLM: Groq or Cerebras API
- TTS: LiveKit or Cartesia or Deepgram
- Storage: Local filesystem (/static folder)

---

## Folder Structure

```
voice-sandbox/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── personas.py
│   │   ├── scenarios.py
│   │   ├── simulations.py
│   │   ├── evaluate.py
│   │   └── evolve.py
│   ├── services/
│   │   ├── llm.py
│   │   ├── tts.py
│   │   ├── evaluation.py
│   │   ├── mutation.py
│   │   └── vector_store.py
│   ├── static/
│   │   └── audio/
│   ├── data.db
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Personas.jsx
│   │   │   ├── Scenarios.jsx
│   │   │   ├── Simulations.jsx
│   │   │   └── Evolution.jsx
│   │   ├── components/
│   │   │   ├── PersonaForm.jsx
│   │   │   ├── ScenarioForm.jsx
│   │   │   ├── AudioPlayer.jsx
│   │   │   └── TranscriptView.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
└── README.md
```

---

## Database Schema

```sql
-- personas table
id INTEGER PRIMARY KEY
name TEXT
personality TEXT
mood TEXT
voice_id TEXT
system_prompt TEXT
created_at TIMESTAMP

-- scenarios table
id INTEGER PRIMARY KEY
name TEXT
context TEXT
goal TEXT
persona_a_id INTEGER (FK personas)
persona_b_id INTEGER (FK personas)
max_turns INTEGER DEFAULT 10
created_at TIMESTAMP

-- simulation_runs table
id INTEGER PRIMARY KEY
scenario_id INTEGER (FK scenarios)
transcript JSON
audio_paths JSON
status TEXT (pending/running/completed/failed)
duration_seconds FLOAT
created_at TIMESTAMP

-- evaluations table
id INTEGER PRIMARY KEY
run_id INTEGER (FK simulation_runs)
scores JSON
overall_score FLOAT
feedback TEXT
created_at TIMESTAMP

-- agent_versions table
id INTEGER PRIMARY KEY
persona_id INTEGER (FK personas)
version INTEGER
system_prompt TEXT
fitness_score FLOAT
parent_version_id INTEGER (FK agent_versions, nullable)
created_at TIMESTAMP
```

---

## Phase 1: FastAPI Setup + Basic Conversation ✅ COMPLETE

### Goal
Two hardcoded agents talk, return transcript.

### Progress
- ✅ Backend structure created
- ✅ Dependencies installed
- ✅ LLM service with Groq integration
- ✅ `/api/simulate` endpoint working
- ✅ Tested successfully

**Note:** Updated model from `llama-3.1-70b-versatile` (decommissioned) to `llama-3.3-70b-versatile`

### Tasks

1. Init FastAPI project in /backend
2. Install dependencies: fastapi, uvicorn, groq or cerebras-cloud-sdk, python-dotenv
3. Create main.py with basic app
4. Create services/llm.py:
   - Function: get_llm_response(system_prompt, messages) -> str
   - Use Groq/Cerebras API
   - Example:
     ```python
     import os
     from groq import Groq

     def get_llm_response(system_prompt, messages=[]):
         if os.getenv("GROQ_API_KEY"):
             client = Groq(api_key=os.getenv("GROQ_API_KEY"))
             model = "llama-3.1-70b-versatile"
         elif os.getenv("CEREBRAS_API_KEY"):
             # Use Cerebras client
             pass
         else:
             raise ValueError("Must set GROQ_API_KEY or CEREBRAS_API_KEY")

         full_messages = [{"role": "system", "content": system_prompt}] + messages

         response = client.chat.completions.create(
             model=model,
             messages=full_messages
         )

         return response.choices[0].message.content
     ```
5. Create /api/simulate endpoint:
   - Input: persona_a_prompt, persona_b_prompt, context (conversation starter), max_turns
   - Logic:
     ```python
     transcript = []
     # Initialize Agent A with context to start conversation
     messages_a = [{"role": "user", "content": context}]
     messages_b = []

     for turn in range(max_turns):
         # Agent A speaks
         response_a = get_llm_response(persona_a_prompt, messages_a)
         transcript.append({"agent": "A", "text": response_a})
         messages_a.append({"role": "assistant", "content": response_a})
         messages_b.append({"role": "user", "content": response_a})

         # Agent B responds
         response_b = get_llm_response(persona_b_prompt, messages_b)
         transcript.append({"agent": "B", "text": response_b})
         messages_b.append({"role": "assistant", "content": response_b})
         messages_a.append({"role": "user", "content": response_b})

     return {"transcript": transcript}
     ```
6. Test via /docs (Swagger UI)

### Output
Working conversation between two LLM agents.

---

## Phase 2: Database + Personas + Scenarios ✅ COMPLETE

### Goal
CRUD for personas and scenarios.

### Progress
- ✅ Database setup with SQLite
- ✅ Models created (Persona, Scenario, SimulationRun, Evaluation, AgentVersion)
- ✅ Pydantic schemas for validation
- ✅ CRUD endpoints for personas
- ✅ CRUD endpoints for scenarios
- ✅ Tables auto-created on startup
- ✅ Tested all CRUD operations

**Database:** data.db created in [backend](backend) folder

### Tasks

1. Install: sqlalchemy, pydantic
2. Create database.py:
   - SQLite connection
   - SessionLocal, engine, Base
3. Create models.py:
   - Persona model
   - Scenario model
4. Create schemas.py:
   - Pydantic schemas for request/response
5. Create routers/personas.py:
   - GET /personas - list all
   - POST /personas - create
   - GET /personas/{id} - get one
   - PUT /personas/{id} - update
   - DELETE /personas/{id} - delete
6. Create routers/scenarios.py:
   - Same CRUD pattern
7. Update main.py to include routers
8. Add table creation on startup:
   ```python
   # In main.py
   from database import engine
   from models import Base

   # Create tables on startup
   @app.on_event("startup")
   def startup():
       Base.metadata.create_all(bind=engine)
   ```
9. Note: system_prompt field in database should contain the full prompt.
   Users can manually craft it or use persona fields (name, personality, mood) as guidelines.

### Output
Full persona and scenario management via API.

---

## Phase 3: Frontend Setup ✅ COMPLETE

### Goal
React frontend to interact with API.

### Progress
- ✅ Vite + React project initialized
- ✅ Tailwind CSS configured
- ✅ React Router setup
- ✅ Pages created (Home, Personas, Scenarios, Simulations)
- ✅ Components created (PersonaForm, ScenarioForm)
- ✅ API integration with axios
- ✅ CORS already configured in backend

**Frontend URL:** http://localhost:5173
**Backend URL:** http://localhost:8000

### Tasks

1. Init Vite + React in /frontend
2. Install: tailwindcss, axios, react-router-dom
3. Setup Tailwind
4. Create pages:
   - Home.jsx: welcome, links to other pages
   - Personas.jsx: list + create form
   - Scenarios.jsx: list + create form (dropdown for persona selection)
   - Simulations.jsx: placeholder
5. Create components:
   - PersonaForm.jsx: name, personality, mood, system_prompt inputs
   - ScenarioForm.jsx: name, context, goal, persona_a, persona_b, max_turns
6. API calls via axios to FastAPI backend
7. Create src/config.js:
   ```javascript
   export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
   ```
8. Create .env in frontend/:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```
9. Setup CORS in FastAPI main.py:
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],  # Vite dev server
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Output
Working frontend for persona/scenario management.

---

## Phase 4: Voice Generation ✅ COMPLETE

### Goal
Convert agent responses to audio.

### Progress
- ✅ Deepgram TTS integration in services/tts.py
- ✅ /api/simulate modified to generate audio per turn
- ✅ Static file serving configured
- ✅ AudioPlayer component created
- ✅ Test simulation page with audio playback
- ✅ Error handling (continues without audio if TTS fails)

**Note:** TTS requires valid DEEPGRAM_API_KEY in .env. If not set, simulations continue without audio.

### Tasks

1. Choose TTS: Deepgram (recommended for MVP - simple API)
2. Create services/tts.py:
   - Function: text_to_speech(text, voice_id) -> audio_file_path
   - Save to /static/audio/{uuid}.mp3
   - Error handling:
     ```python
     import uuid
     from pathlib import Path

     def text_to_speech(text, voice_id):
         try:
             # TTS API call here
             audio_filename = f"{uuid.uuid4()}.mp3"
             audio_path = Path("static/audio") / audio_filename
             # Save audio to audio_path
             return str(audio_path)
         except Exception as e:
             print(f"TTS failed: {e}")
             return None  # Continue simulation without audio
     ```
3. Add voice_id field to Persona model
4. Modify /api/simulate:
   - After each turn, generate audio (with error handling)
   - Store audio paths in transcript
   - Return audio_paths array
   ```python
   # In simulation loop
   audio_path = text_to_speech(response_a, persona_a.voice_id)
   transcript.append({
       "agent": "A",
       "text": response_a,
       "audio": audio_path  # May be None if TTS failed
   })
   ```
5. Serve static files in FastAPI:
   ```python
   from pathlib import Path
   from fastapi.staticfiles import StaticFiles

   BASE_DIR = Path(__file__).parent
   app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
   ```
6. Frontend AudioPlayer.jsx:
   - Play individual turns
   - Play full conversation
   - Show waveform (optional, keep simple)

### Output
Simulations with playable audio.

---

## Phase 5: Simulation Logs ✅ COMPLETE

### Goal
Store and view simulation history.

### Progress
- ✅ SimulationRun model created
- ✅ routers/simulations.py with full CRUD
- ✅ Simulation execution with status tracking
- ✅ Frontend list + detail view
- ✅ Audio playback integration

### Tasks

1. Add SimulationRun model to models.py
2. Create routers/simulations.py:
   - POST /simulations/run - execute simulation, store result
   - GET /simulations - list all runs
   - GET /simulations/{id} - get details
3. Update simulate logic:
   - Create SimulationRun record before starting
   - Update status: pending -> running -> completed/failed
   - Store transcript JSON, audio_paths JSON
4. Frontend Simulations.jsx:
   - List all runs (scenario name, status, date)
   - Click to view detail
   - Detail page: transcript + audio player + metadata

### Output
Full simulation history with playback.

---

## Post-Phase 5 Improvements ✅ COMPLETE

### 1. Multi-Provider LLM Support (Cerebras + Groq)
**Problem:** Groq rate limits (100k tokens/day) too restrictive

**Solution:** Added easy provider switching in `services/llm.py`
```python
# Line 9: Change this variable to switch providers
PROVIDER = "cerebras"  # Options: "groq" or "cerebras"
```

**Changes:**
- Added `cerebras-cloud-sdk` to requirements.txt
- Modified `get_llm_response()` to support both providers
- Groq: `llama-3.3-70b-versatile`
- Cerebras: `llama-3.3-70b`

**Earlier approach:** Used environment variable `LLM_PROVIDER`
**Current approach:** Hardcoded `PROVIDER` variable for simplicity

---

### 2. Deepgram TTS SDK v5 Compatibility
**Problem:** Multiple API breaking changes in Deepgram SDK v5

**Errors encountered:**
1. ❌ `ImportError: cannot import name 'SpeakOptions'` - Class removed in v5
2. ❌ `'SpeakClient' has no attribute 'v'` - API structure changed
3. ❌ `'SpeakClient' has no attribute 'rest'` - Incorrect migration attempt

**Final fix in `services/tts.py` line 34:**
```python
response = deepgram.speak.v("1").save(str(audio_path), {"text": text}, {"model": voice})
```

**Earlier approach:** Used `SpeakOptions` class
**Current approach:** Use dict for options, `.speak.v("1").save()` API

---

### 3. Verbose Dialogue Fix ✅ NEW
**Problem:** LLM generating theatrical 500+ word monologues with stage directions like:
- "(Pause for response)"
- "(Listen to Sarah's response)"
- Unnatural scripted dialogue

**Goal:** Natural phone-like conversation (1-3 sentences per turn)

**Solution:**

1. **Added `max_tokens` parameter in `services/llm.py` (line 13):**
```python
def get_llm_response(system_prompt, messages=[], max_tokens=None):
    # ... existing code ...

    params = {
        "model": model,
        "messages": full_messages
    }
    if max_tokens:
        params["max_tokens"] = max_tokens

    response = client.chat.completions.create(**params)
```

2. **Enhanced prompts in `routers/simulations.py` (lines 58-66, 78-80):**
```python
# Conciseness instruction for natural dialogue
concise_instruction = """IMPORTANT: Keep responses SHORT and NATURAL (1-3 sentences max).
Speak directly as your character without stage directions, labels, or parenthetical notes.
Act like a real conversation, not a script."""

for turn in range(scenario.max_turns):
    # Agent A speaks
    enhanced_prompt_a = f"{concise_instruction}\n\n{persona_a.system_prompt}"
    response_a = get_llm_response(enhanced_prompt_a, messages_a, max_tokens=150)

    # Agent B responds
    enhanced_prompt_b = f"{concise_instruction}\n\n{persona_b.system_prompt}"
    response_b = get_llm_response(enhanced_prompt_b, messages_b, max_tokens=150)
```

**Token limit:** 150 tokens ≈ 100 words per turn

**Earlier approach:** No token limit, no conciseness instruction
**Current approach:** Token capping + explicit system prompt enhancement

---

## Phase 6: Evaluation System

### Goal
Score conversations automatically.

### Tasks

1. Create services/evaluation.py:
   - Function: evaluate_conversation(transcript, criteria) -> scores
   - Use LLM-as-judge pattern:
     ```python
     import re
     import json

     def evaluate_conversation(transcript, goal):
         prompt = f"""Evaluate this conversation:
         {json.dumps(transcript)}

         Goal: {goal}

         Score 1-10 for:
         - task_completion: Did they achieve the goal?
         - naturalness: Does it sound natural?
         - goal_achieved: How well was the goal met?

         Return ONLY valid JSON in this exact format:
         {{"task_completion": X, "naturalness": X, "goal_achieved": X, "feedback": "..."}}"""

         response = get_llm_response(prompt)

         # Extract JSON from response (handles markdown wrapping)
         json_match = re.search(r'\{.*\}', response, re.DOTALL)
         if json_match:
             scores = json.loads(json_match.group())
         else:
             # Fallback if parsing fails
             scores = {"task_completion": 5, "naturalness": 5, "goal_achieved": 5, "feedback": "Parse error"}

         return scores
     ```
2. Add Evaluation model
3. Create routers/evaluate.py:
   - POST /evaluate/{run_id} - evaluate a run
   - GET /evaluations/{run_id} - get evaluation
4. Auto-run evaluation after simulation completes
5. Frontend: show scores on simulation detail page

### Output
Automated scoring with feedback.

---

## Phase 7: Vector Store + Search

### Goal
Store conversation embeddings, find patterns.

### Tasks

1. Install chromadb
2. Create services/vector_store.py:
   ```python
   import chromadb
   from chromadb.utils import embedding_functions

   # Initialize ChromaDB client
   client = chromadb.PersistentClient(path="./chroma_db")

   # Use default embedding model (all-MiniLM-L6-v2)
   embedding_fn = embedding_functions.DefaultEmbeddingFunction()

   def init_collection():
       return client.get_or_create_collection(
           name="conversations",
           embedding_function=embedding_fn
       )

   def add_conversation(run_id, transcript):
       collection = init_collection()
       # Embed full transcript as single document
       full_text = "\n".join([f"{t['agent']}: {t['text']}" for t in transcript])
       collection.add(
           ids=[str(run_id)],
           documents=[full_text],
           metadatas=[{"run_id": run_id}]
       )

   def search_similar(query, k=5):
       collection = init_collection()
       results = collection.query(query_texts=[query], n_results=k)
       return results
   ```
3. After each simulation, embed and store transcript
4. API endpoint: GET /search?q=... - find similar conversations
5. Use for: finding failure patterns, similar scenarios

### Output
Searchable conversation history.

---

## Phase 8: DGM Self-Improvement Loop

### Goal
Agents evolve based on performance.

### Tasks

1. Add AgentVersion model
2. Create services/mutation.py:
   ```python
   import json

   def mutate_prompt(current_prompt, all_evaluations):
       """
       Mutate based on aggregated feedback from multiple simulations
       """
       # Aggregate common feedback
       all_feedback = [eval['feedback'] for eval in all_evaluations]
       avg_scores = {
           'task_completion': sum(e['task_completion'] for e in all_evaluations) / len(all_evaluations),
           'naturalness': sum(e['naturalness'] for e in all_evaluations) / len(all_evaluations),
           'goal_achieved': sum(e['goal_achieved'] for e in all_evaluations) / len(all_evaluations)
       }

       mutation_prompt = f"""
       Current agent prompt: {current_prompt}

       Average scores across {len(all_evaluations)} simulations:
       - Task completion: {avg_scores['task_completion']}/10
       - Naturalness: {avg_scores['naturalness']}/10
       - Goal achieved: {avg_scores['goal_achieved']}/10

       Common feedback:
       {json.dumps(all_feedback, indent=2)}

       Generate an improved system prompt that addresses these issues.
       Keep the same core personality, but fix the problems.
       Return ONLY the new system prompt, nothing else.
       """
       return get_llm_response(mutation_prompt)
   ```
3. Create routers/evolve.py:
   - POST /evolve/{persona_id} - run evolution cycle:
     ```python
     # Configuration for MVP
     N_SIMULATIONS = 5  # Run 5 test simulations
     FAILURE_THRESHOLD = 6.0  # Scores below 6 trigger mutation
     N_MUTATIONS = 3  # Generate 3 variants

     # Get current version
     # Run N_SIMULATIONS simulations with current prompt
     # Evaluate all
     # Calculate average overall_score
     # If avg_score < FAILURE_THRESHOLD:
     #     Generate N_MUTATIONS mutations
     #     Test each mutation (run 3 sims each)
     #     Pick mutation with highest avg score
     #     Save as new version
     # Return version comparison
     ```
   - GET /versions/{persona_id} - list all versions
   - POST /versions/{version_id}/activate - set as current
4. Frontend Evolution.jsx:
   - Select persona
   - Run evolution button
   - Version history list
   - Compare versions
   - Fitness score chart over generations

### Output
Self-improving agents via evolution loop.

---

## API Endpoints Summary

```
# Personas
GET    /api/personas
POST   /api/personas
GET    /api/personas/{id}
PUT    /api/personas/{id}
DELETE /api/personas/{id}

# Scenarios
GET    /api/scenarios
POST   /api/scenarios
GET    /api/scenarios/{id}
PUT    /api/scenarios/{id}
DELETE /api/scenarios/{id}

# Simulations
POST   /api/simulations/run
GET    /api/simulations
GET    /api/simulations/{id}

# Evaluation
POST   /api/evaluate/{run_id}
GET    /api/evaluations/{run_id}

# Search
GET    /api/search?q=...

# Evolution
POST   /api/evolve/{persona_id}
GET    /api/versions/{persona_id}
POST   /api/versions/{version_id}/activate
```

---

## Environment Variables

```
# backend/.env
GROQ_API_KEY=xxx
# or CEREBRAS_API_KEY=xxx

# TTS (using Deepgram for MVP)
DEEPGRAM_API_KEY=xxx

# Database
DATABASE_URL=sqlite:///./data.db

# Environment
ENVIRONMENT=development
```

---

## Requirements

### backend/requirements.txt
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
python-dotenv
groq
chromadb
httpx
python-multipart
deepgram-sdk
```

---

## Start Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Implementation Order

1. Phase 1: Get two agents talking
2. Phase 2: Add database, personas, scenarios
3. Phase 3: Build frontend
4. Phase 4: Add voice
5. Phase 5: Store simulation logs
6. Phase 6: Add evaluation
7. Phase 7: Add vector search
8. Phase 8: DGM evolution loop

Start with Phase 1. Keep each phase working before moving to next.
```

