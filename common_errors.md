# Common Errors - Voice AI Sandbox Platform

## Database & CORS Errors

### ❌ Error: CORS header 'Access-Control-Allow-Origin' missing (500 status)
**Full error:**
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://localhost:8000/api/personas/.
(Reason: CORS header 'Access-Control-Allow-Origin' missing). Status code: 500.
```

**Root cause:** Backend crashing with 500 due to Pydantic validation failing on NULL foreign keys in database
- Scenarios with NULL `persona_a_id` or `persona_b_id`
- SimulationRuns with NULL `scenario_id`

**Fix:** Clean up invalid database records:
```python
# Delete scenarios with null persona IDs
db.query(Scenario).filter((Scenario.persona_a_id == None) | (Scenario.persona_b_id == None)).delete()

# Delete simulations with null scenario IDs
db.query(SimulationRun).filter(SimulationRun.scenario_id == None).delete()
db.commit()
```

**Prevention:** Always validate foreign keys before creating records

---

## Deepgram TTS SDK v5 Migration Errors

### ❌ Error 1: ImportError - SpeakOptions not found
**Full error:**
```
ImportError: cannot import name 'SpeakOptions' from 'deepgram'
```

**Root cause:** Deepgram SDK v5 removed the `SpeakOptions` class

**Fix:** Use dict instead of class:
```python
# ❌ Old (SDK v4)
from deepgram import DeepgramClient, SpeakOptions
options = SpeakOptions(model=voice)

# ✅ New (SDK v5)
from deepgram import DeepgramClient
options = {"model": voice}
```

---

### ❌ Error 2: 'SpeakClient' object has no attribute 'v'
**Full error:**
```
TTS failed: 'SpeakClient' object has no attribute 'v'
```

**Root cause:** Attempted to use `deepgram.speak.v("1")` but API structure changed in v5

**Attempted fix (WRONG):**
```python
response = deepgram.speak.rest.v("1").save(...)  # This doesn't work
```

---

### ❌ Error 3: 'SpeakClient' object has no attribute 'rest'
**Full error:**
```
TTS failed: 'SpeakClient' object has no attribute 'rest'
```

**Root cause:** Previous migration attempt was incorrect

**✅ Correct fix (SDK v5 API):**
```python
# services/tts.py line 34
response = deepgram.speak.v("1").save(str(audio_path), {"text": text}, {"model": voice})
```

**Reference:** [Deepgram SDK v5 GitHub examples](https://github.com/deepgram/deepgram-python-sdk)

---

## LLM Provider Errors

### ❌ Error: Groq rate limit exceeded
**Full error:**
```
Rate limit reached for model 'llama-3.3-70b-versatile' in organization 'org_01jvp1tkkwffsb8aa7f1nmm7h1'
service tier 'on_demand_on tokens per day (TPD): Limit 100000, Used 99725
```

**Root cause:** Groq free tier has 100k tokens/day limit

**Fix:** Switch to Cerebras provider
```python
# services/llm.py line 9
PROVIDER = "cerebras"  # Switch from "groq" to "cerebras"
```

**Prevention:** Use Cerebras for development (higher rate limits)

---

## Conversation Quality Issues

### ❌ Problem: Verbose theatrical dialogue with stage directions
**Symptoms:**
- 500+ word monologues per turn
- Stage directions: "(Pause for response)", "(Listen to Sarah's response)"
- Unnatural scripted dialogue instead of conversation

**Root cause:** LLM lacks token limits and conciseness instructions

**Fix:** Add token capping + enhanced system prompts

**Solution 1 - Add max_tokens parameter (`services/llm.py`):**
```python
def get_llm_response(system_prompt, messages=[], max_tokens=None):
    params = {
        "model": model,
        "messages": full_messages
    }
    if max_tokens:
        params["max_tokens"] = max_tokens

    response = client.chat.completions.create(**params)
```

**Solution 2 - Prepend conciseness instruction (`routers/simulations.py`):**
```python
concise_instruction = """IMPORTANT: Keep responses SHORT and NATURAL (1-3 sentences max).
Speak directly as your character without stage directions, labels, or parenthetical notes.
Act like a real conversation, not a script."""

enhanced_prompt_a = f"{concise_instruction}\n\n{persona_a.system_prompt}"
response_a = get_llm_response(enhanced_prompt_a, messages_a, max_tokens=150)
```

**Token limit:** 150 tokens ≈ 100 words per turn

---

## Backend Server Issues

### ❌ Problem: Changes not reflected after editing code
**Root cause:** uvicorn auto-reload sometimes gets stuck

**Fix:** Manually kill and restart backend:
```bash
# Kill all running backend processes
# Then restart:
cd backend
uvicorn main:app --reload --port 8000
```

**Alternative:** Check for multiple running instances and kill duplicates

---

### ❌ Error: 404 on /api/simulations/
**Root cause:** Missing `__init__.py` in routers folder

**Fix:** Create empty file:
```bash
# backend/routers/__init__.py
# (empty file)
```

**Why:** Python requires `__init__.py` to treat directory as package

---

## Frontend Issues

### ❌ Problem: Frontend on wrong port (5174 instead of 5173)
**Root cause:** Vite auto-increments port if 5173 is busy

**Fix:** Update CORS to allow both ports:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Quick Troubleshooting Checklist

When simulations fail:
1. ✅ Check backend logs for TTS errors
2. ✅ Verify DEEPGRAM_API_KEY is set in .env
3. ✅ Check database for NULL foreign keys
4. ✅ Verify LLM provider (Groq vs Cerebras) in services/llm.py line 9
5. ✅ Restart backend if auto-reload stuck
6. ✅ Check CORS ports match frontend dev server
7. ✅ Verify routers/__init__.py exists

When audio doesn't play:
1. ✅ Check transcript.audio is not null
2. ✅ Verify static/audio/ directory exists and has .mp3 files
3. ✅ Check backend static file serving is mounted
4. ✅ Inspect browser console for 404 errors on audio files
