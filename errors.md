# Common Errors - Voice AI Sandbox

This file tracks errors encountered during development and their solutions.

---

## Phase 1: Basic Conversation

### Error 1: Model Decommissioned
**Error:** `groq.BadRequestError: model 'llama-3.1-70b-versatile' has been decommissioned`

**Solution:** Updated to `llama-3.3-70b-versatile` in [services/llm.py](backend/services/llm.py:12)

---

## Phase 2: Database + Personas + Scenarios

(No errors encountered)

---

## Phase 3: Frontend Setup

(No errors encountered)

---

## Phase 4: Voice Generation

(No errors encountered)

**Note:** TTS is optional - if DEEPGRAM_API_KEY not set, simulations run without audio.

---

## Phase 5: Simulation Logs

### Error 2: Deepgram SDK Import Error
**Error:** `ImportError: cannot import name 'SpeakOptions' from 'deepgram'`

**Cause:** Deepgram SDK v5 changed the API - `SpeakOptions` class removed

**Solution:** Use plain dictionary for options instead:
```python
# Before (doesn't work with v5):
from deepgram import DeepgramClient, SpeakOptions
options = SpeakOptions(model=voice)

# After (works with v5):
from deepgram import DeepgramClient
options = {"model": voice}
```
Fixed in [services/tts.py](backend/services/tts.py:34)

### Error 3: Missing __init__.py in routers/
**Error:** `404 Not Found` on `/api/simulations/` endpoint

**Cause:** Missing `__init__.py` file in `backend/routers/` directory

**Solution:** Created empty `__init__.py` file in `backend/routers/` to make it a Python package

---
