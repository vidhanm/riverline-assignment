# Self-Evolving Voice Agent Platform

A Darwin Gödel Machine-inspired platform that evolves debt collection voice agents through automated testing and self-improvement. Built for the Riverline AI Engineer Assignment.

## 🎯 Overview

This platform creates AI voice agents that continuously improve through simulated conversations, automated evaluation, and evolutionary prompt rewriting. The system tests agents across multiple customer personas, identifies failures, and generates improved versions using LLM-as-mutation-generator.

**Key Innovation:** Agents evolve by learning from success/failure patterns in vector-stored conversation history, without human intervention.

---

## ✨ Features

### Part 1: Base Voice Agent
- ✅ **Multi-Persona Simulation**: 10 personas (1 debt collector + 9 customer types)
- ✅ **Text-Based Conversations**: LLM-driven dialogue with configurable prompts
- ✅ **TTS Integration**: Deepgram audio generation (optional, can be disabled)
- ✅ **Multi-Scenario Testing**: 9 scenarios testing different customer behaviors
- ✅ **Automated Evaluation**: LLM-as-judge scoring on 3 metrics:
  - Task completion (payment agreement reached?)
  - Conversational naturalness (repetitions, hallucinations, tone)
  - Goal achievement (compliance, no threats)

### Part 2: Darwin Gödel Evolution
- ✅ **Agent Archive**: Persistent version history with parent-child lineage
- ✅ **Mutation System**:
  - Generates 3 prompt variants per evolution cycle
  - Uses vector search to find success/failure examples
  - Tests mutations across 5 scenarios (25+ simulations per cycle)
- ✅ **Explainability**: Every mutation includes:
  - Reasoning prompt (why this change?)
  - Success examples learned from
  - Failure examples avoided
  - Evaluator feedback addressed
- ✅ **Tree Visualization**: SVG graph showing evolution branches
- ✅ **Termination Policy**: Evolves until fitness > 8.5/10 or no improvement

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy + SQLite
- ChromaDB (vector embeddings)
- Groq/Cerebras (LLM APIs)
- Deepgram (TTS)

**Frontend:**
- React + Vite
- Tailwind CSS
- Axios
- React Router

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key
CEREBRAS_API_KEY=your_cerebras_api_key  # Optional alternative
DEEPGRAM_API_KEY=your_deepgram_key     # Optional for TTS
DISABLE_TTS=true                        # Set false to enable audio
EOF

# Run database migrations
python migrate_mutation_metadata.py
python upgrade_db_schema.py  # If needed

# Seed initial data
python seed_debt_collection.py
python seed_scenarios.py
python seed_difficult_personas.py
python seed_difficult_scenarios.py

# Start server
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🚀 Usage

### 1. Create Personas & Scenarios
- Navigate to **Personas** page
- Create agent personas (e.g., debt collector Marcus)
- Create customer personas (angry, evasive, cooperative, etc.)
- Navigate to **Scenarios** page
- Define conversation contexts (loan amount, days overdue, etc.)

### 2. Run Simulations
- Go to **Simulations** page
- Select a scenario
- Click "Run Simulation"
- View transcript + audio playback
- Check automated evaluation scores

### 3. Evolve Agents
- Go to **Evolution Lab**
- Select persona (e.g., Marcus)
- Select multiple scenarios to test (checkbox selection)
- Click "Evolve Now"
- **Wait ~8 minutes** (runs 20+ simulations)
- View results:
  - 🌳 **Tree View**: Visual evolution graph
  - 📋 **List View**: Version history
  - 🧠 **Reasoning Panel**: Click version → see mutation logic

### 4. Explore Evolution Reasoning
- Click on any version in the tree
- Switch between mutation tabs (Mutation 1, 2, 3)
- View:
  - Performance metrics
  - Scenarios tested
  - Evaluator feedback used
  - ✅ Success examples learned from
  - ❌ Failure patterns avoided
  - 🧠 Full LLM prompt sent for mutation generation

---

## 📁 Project Structure

```
voice-ai-sandbox/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── database.py                # DB connection
│   ├── routers/
│   │   ├── personas.py            # Persona CRUD
│   │   ├── scenarios.py           # Scenario CRUD
│   │   ├── simulations.py         # Run conversations
│   │   ├── evolve.py              # Evolution API
│   │   └── search.py              # Vector search
│   ├── services/
│   │   ├── llm.py                 # Groq/Cerebras integration
│   │   ├── tts.py                 # Deepgram TTS
│   │   ├── evaluation.py          # LLM-as-judge
│   │   ├── mutation.py            # Prompt evolution logic
│   │   └── vector_store.py        # ChromaDB wrapper
│   ├── static/audio/              # Generated MP3 files
│   ├── data.db                    # SQLite database
│   └── chroma_db/                 # Vector embeddings
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Personas.jsx
│   │   │   ├── Scenarios.jsx
│   │   │   ├── Simulations.jsx
│   │   │   └── Evolution.jsx      # Evolution Lab UI
│   │   ├── components/
│   │   │   ├── EvolutionTree.jsx  # Tree visualization
│   │   │   └── MutationDetails.jsx # Reasoning panel
│   │   ├── App.jsx
│   │   └── config.js
│   └── package.json
│
├── guide.md                       # Development log
├── common_errors.md               # Error troubleshooting
└── README.md                      # This file
```

---

## 🔌 API Endpoints

### Personas
```
GET    /api/personas              # List all
POST   /api/personas              # Create
GET    /api/personas/{id}         # Get one
PUT    /api/personas/{id}         # Update
DELETE /api/personas/{id}         # Delete
```

### Scenarios
```
GET    /api/scenarios             # List all
POST   /api/scenarios             # Create
GET    /api/scenarios/{id}        # Get one
PUT    /api/scenarios/{id}        # Update
DELETE /api/scenarios/{id}        # Delete
```

### Simulations
```
POST   /api/simulations/run       # Execute conversation
GET    /api/simulations           # List history
GET    /api/simulations/{id}      # Get transcript
```

### Evaluation
```
POST   /api/evaluate/{run_id}     # Score conversation
GET    /api/evaluations/{run_id}  # Get scores
```

### Evolution
```
POST   /api/evolve/{persona_id}?scenario_ids=1,2,3
       # Run evolution cycle (returns new version)

GET    /api/evolve/versions/{persona_id}
       # Get version history with mutation metadata

POST   /api/evolve/versions/{version_id}/activate
       # Set version as current
```

---

## 🎓 Assignment Compliance

### Part 1 Requirements ✅
- [x] Voice agent (text-based simulation)
- [x] Configurable prompts per agent version
- [x] Modular architecture (prompt/logic/evaluation layers)
- [x] 5+ customer personas (9 created: angry, evasive, curious, cooperative, desperate, threatening, dismissive, blame-shifting, silent)
- [x] Randomized persona testing
- [x] 3 automated metrics (task_completion, naturalness, goal_achieved)
- [x] No manual scoring (LLM-as-judge)

### Part 2 Requirements ✅
- [x] **Darwinian Agent Archive**: SQLite + version tracking + parent lineage
- [x] **Prompt Rewriting Loop**:
  - Vector search retrieves success/failure examples
  - LLM generates mutations with reasoning
  - 3 variants tested per cycle
  - Best performer promoted
- [x] **Termination Policy**: Threshold 8.5/10 or plateau detection
- [x] **Explainability**:
  - Every mutation has rationale (stored in `mutation_metadata`)
  - Links to failures addressed (success/failure examples)
  - Full reasoning prompt logged
  - UI displays all reasoning data

### Submission Checklist
- [x] GitHub repo (public): [riverline-assignment](https://github.com/vidhanm/riverline-assignment)
- [x] Detailed README (this file)
- [ ] Audio recording of voice conversation (TODO)
- [ ] 2-3 minute demo video (TODO)
- [x] Logs: 40+ simulation runs, 2 agent versions, mutation attempts

---

## 🧪 Example Evolution Flow

1. **Baseline Testing**
   - Marcus v1 tested across 5 scenarios
   - Average score: 3.5/10 (fails with angry/evasive customers)

2. **Mutation Generation**
   - Vector search finds successful approaches from DB
   - LLM generates 3 improved prompts based on:
     - Feedback: "Too aggressive, lacks empathy"
     - Success pattern: "Acknowledge customer frustration first"
     - Failure pattern: "Demanding immediate payment"

3. **Mutation Testing**
   - Mutation 1: 4.2/10 (better tone, still pushy)
   - Mutation 2: 6.1/10 (empathetic, solution-focused) ⭐ WINNER
   - Mutation 3: 3.8/10 (too passive)

4. **Version Saved**
   - Marcus v2 activated with Mutation 2 prompt
   - Tree shows: v1 → v2 (+2.6 improvement)
   - Metadata stored for future evolution

---

## 🔧 Configuration

### Switch LLM Provider
Edit `backend/services/llm.py`:
```python
PROVIDER = "cerebras"  # Options: "groq" or "cerebras"
```

### Disable Audio Generation
```bash
# In backend/.env
DISABLE_TTS=true
```

### Change Evolution Parameters
Edit `backend/routers/evolve.py`:
```python
N_BASELINE_SIMS = 5      # Baseline test count
FAILURE_THRESHOLD = 8.5  # Evolution trigger
N_MUTATIONS = 3          # Variants per cycle
N_MUTATION_TESTS = 5     # Tests per variant
```

---

## 🐛 Common Issues

See [common_errors.md](common_errors.md) for troubleshooting.

**Quick fixes:**
- `ImportError: SpeakOptions` → Update Deepgram SDK or set `DISABLE_TTS=true`
- `chromadb.errors.NotEnoughElementsException` → Delete `chroma_db/` and re-run
- Evolution taking too long → Reduce `N_MUTATION_TESTS` or disable TTS
- No versions showing → Run evolution at least once

---

## 📊 Performance

**Typical Evolution Cycle:**
- 5 baseline sims + (3 mutations × 5 tests) = 20 simulations
- ~8 minutes with TTS disabled
- ~15 minutes with TTS enabled

**Database Size:**
- 40 simulations ≈ 5 MB (transcripts + audio paths)
- Vector DB ≈ 2 MB (conversation embeddings)

