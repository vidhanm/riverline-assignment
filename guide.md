# Voice AI Sandbox Platform - Implementation Guide

## Overview
Voice AI simulation platform where two AI personas have conversations, generate audio, store logs, evaluate performance, and self-improve via DGM (Darwin Gödel Machine).

## Tech Stack
- **Frontend:** React + Vite + Tailwind
- **Backend:** FastAPI (Python)
- **Database:** SQLite + SQLAlchemy
- **Vector DB:** ChromaDB (local)
- **LLM:** NVIDIA / Groq / Cerebras (switchable)
- **TTS:** Deepgram (English), Sarvam (Hindi)
- **Voice Agent:** LiveKit

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | FastAPI + Basic Conversation | ✅ Complete |
| 2 | Database + Personas + Scenarios | ✅ Complete |
| 3 | React Frontend | ✅ Complete |
| 4 | Voice Generation (Deepgram TTS) | ✅ Complete |
| 5 | Simulation Logs | ✅ Complete |
| 6 | Evaluation System | ✅ Complete |
| 7 | Vector Store + Search | ✅ Complete |
| 8 | DGM Self-Improvement Loop | ✅ Complete |
| 9 | LiveKit Voice Agent | ✅ Complete |

---

## Key Configuration

### LLM Provider Switch
In `services/llm.py` line 9:
```python
PROVIDER = "nvidia"  # Options: "nvidia", "groq", "cerebras"
```

### Audio Control
In `backend/.env`:
```bash
DISABLE_TTS=true   # Faster simulations, no audio
DISABLE_TTS=false  # Enable audio generation
```

### Evolution Thresholds
In `routers/evolve.py`:
- `FAILURE_THRESHOLD = 8.5` - Triggers evolution for assignment demo
- `N_MUTATION_TESTS = 5` - Fair comparison across all scenarios
- `PLATEAU_WINDOW = 3` - Generations to check for stagnation
- `PLATEAU_THRESHOLD = 0.2` - Minimum improvement required

---

## Important Design Decisions

### 1. Deepgram TTS SDK v5 Fix
**Problem:** Breaking changes in Deepgram SDK v5
**Solution in `services/tts.py`:**
```python
response = deepgram.speak.v("1").save(str(audio_path), {"text": text}, {"model": voice})
```

### 2. Verbose Dialogue Fix
**Problem:** LLM generating 500+ word monologues with stage directions
**Solution:** Token limit (150) + conciseness instruction in prompts

### 3. Zero-Shot Learning for Evolution
**Problem:** Marcus had "insider knowledge" about customer personalities (baseline too easy at 7.3/10)
**Solution:** 
- Scenarios now say "No prior behavioral data" instead of revealing personality
- Marcus discovers personality during call
- Result: Baseline drops to ~4-5/10, evolution learns real adaptive skills

### 4. Chameleon Personas (NEW)
**Problem:** Trained against known, static personas but real users are unknown
**Solution:** Created personas that change behavior mid-conversation:
- Alex: Hostile → Cooperative (when treated with respect)
- Maya: Evasive → Desperate (as call progresses)
- Chris: Mood swings throughout
- Priya: Disputes → Settles

### 5. Behavioral Detection (NEW)
**Problem:** Marcus prompt was only ~20 words, no adaptation strategy
**Solution:** Enhanced to ~400 words with:
- HOSTILE/EVASIVE/DESPERATE/COOPERATIVE/SILENT detection signals
- Specific strategies for each behavior type
- FDCPA compliance guidelines

---

## Evaluation Metrics (Assignment-Aligned)

1. **goal_completion** (1-10): Did borrower agree to pay?
2. **conversational_quality** (1-10): Repetitions, hallucinations, tone
3. **compliance** (1-10): Avoid threats, illegal phrasing, harassment
4. **adaptation_quality** (1-10): How well agent adapted to customer behavior changes

**Overall Score:** Average of all 4 metrics

---

## API Endpoints

```
# Personas
GET/POST         /api/personas
GET/PUT/DELETE   /api/personas/{id}

# Scenarios
GET/POST         /api/scenarios
GET/PUT/DELETE   /api/scenarios/{id}

# Simulations
POST   /api/simulations/run
GET    /api/simulations
GET    /api/simulations/{id}

# Legacy Simulate
POST   /api/simulate

# Search
GET    /api/search?q=...

# Evolution
POST   /api/evolve/{persona_id}
GET    /api/evolve/versions/{persona_id}
POST   /api/evolve/versions/{version_id}/activate
GET    /api/evolve/plateau/{persona_id}

# Voice
POST   /api/voice/token
```

---

## Environment Variables

```bash
# backend/.env
GROQ_API_KEY=xxx
CEREBRAS_API_KEY=xxx
NVIDIA_API_KEY=xxx
DEEPGRAM_API_KEY=xxx
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=xxx
LIVEKIT_API_SECRET=xxx
DISABLE_TTS=true
```

---

## Start Commands

```bash
# Backend API
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Voice Agent (separate terminal)
cd backend
python voice_agent.py dev

# Frontend
cd frontend
npm install
npm run dev

# Seed Database (run once)
cd backend/scripts
python seed_all.py
```

---

## Database Schema

**Tables:** personas, scenarios, simulation_runs, evaluations, agent_versions

Key fields:
- `agent_versions.mutation_metadata` - JSON with success/failure examples, feedback
- `agent_versions.reasoning_prompt` - Full LLM prompt for transparency
- `evaluations.structured_issues` - Granular feedback by category

---

## Hindi Language Support

**Enable:**
```bash
cd backend/scripts
python enable_hindi.py
```

**Limitation:** Audio still English (Deepgram doesn't support Hindi TTS)

---

## Difficult Scenario Training

**Problem:** Initial scenarios had polarized scores (3/10 vs 9.7/10)

**Solution:** Added more difficult personas:
- James (Threatening) - Hostile, threatens to sue
- Karen (Dismissive) - Condescending, mocks Marcus
- Tony (Blame-Shifting) - Blames bank/economy
- Emma (Silent) - One-word answers

**For evolution:** Select ONLY hard scenarios (IDs: 1,2,6,7,8,9) to train on weaknesses

---

## Evolution Visualization

- **Tree View:** SVG lines connecting parent→child versions
- **Solid line** = improvement, **Dashed** = regression
- **Yellow circles** = winning mutations
- **Mutation Details Panel:** Shows feedback, success/failure examples, reasoning prompt

---

## Submission Checklist

- [x] GitHub repo with detailed README
- [x] Self-modifying voice agent (DGM evolution loop)
- [x] Version archive with evaluation scores and prompt changes
- [x] LiveKit voice agent working locally
- [ ] Audio recording of talking with voice agent
- [ ] 2-3 minute demo video
