# Troubleshooting Guide - Voice AI Sandbox

Quick reference for common errors and their solutions.

---

## Quick Checklist

When simulations fail:
1. ✅ Check backend logs for errors
2. ✅ Verify API keys in `.env` (DEEPGRAM_API_KEY, NVIDIA_API_KEY, etc.)
3. ✅ Check LLM provider setting in `services/llm.py`
4. ✅ Restart backend if auto-reload stuck
5. ✅ Check CORS ports match frontend

When audio doesn't play:
1. ✅ Check `static/audio/` directory exists
2. ✅ Verify DEEPGRAM_API_KEY is set
3. ✅ Inspect browser console for 404 errors

---

## LLM Provider Errors

### Groq Rate Limit Exceeded
```
Rate limit reached for model... Limit 100000, Used 99725
```
**Fix:** Switch to different provider in `services/llm.py`:
```python
PROVIDER = "nvidia"  # or "cerebras"
```

### Model Decommissioned
```
groq.BadRequestError: model 'llama-3.1-70b-versatile' has been decommissioned
```
**Fix:** Update to `llama-3.3-70b-versatile`

---

## Deepgram TTS Errors (SDK v5)

### ImportError: SpeakOptions not found
```
ImportError: cannot import name 'SpeakOptions' from 'deepgram'
```
**Fix:** SDK v5 uses dict instead of class:
```python
# Correct v5 API:
response = deepgram.speak.v("1").save(str(audio_path), {"text": text}, {"model": voice})
```

---

## Database & CORS Errors

### CORS 500 Error
```
Cross-Origin Request Blocked... Status code: 500
```
**Cause:** Backend crashing due to NULL foreign keys in database

**Fix:** Clean up invalid records or check model validation

### 404 on API Endpoints
```
404 Not Found on /api/simulations/
```
**Fix:** Ensure `backend/routers/__init__.py` exists (can be empty)

---

## Frontend Issues

### Wrong Port (5174 instead of 5173)
**Fix:** Update CORS in `backend/main.py`:
```python
allow_origins=["http://localhost:5173", "http://localhost:5174"]
```

---

## Conversation Quality Issues

### Verbose Theatrical Dialogue
**Symptoms:** 500+ word responses, stage directions like "(Pause)"

**Fix:** Already implemented in codebase:
- Token limit: 150 tokens per turn
- Conciseness instruction prepended to prompts

---

## Backend Server Issues

### Changes Not Reflected
**Fix:** Kill and restart backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

---

## Environment Variables (.env)

Required keys:
```
NVIDIA_API_KEY=xxx       # Primary LLM (or use GROQ/CEREBRAS)
DEEPGRAM_API_KEY=xxx     # TTS (optional - simulations work without audio)
LIVEKIT_API_KEY=xxx      # Voice agent
LIVEKIT_API_SECRET=xxx   # Voice agent
LIVEKIT_URL=xxx          # Voice agent
SARVAM_API_KEY=xxx       # Hindi TTS (optional)
```
