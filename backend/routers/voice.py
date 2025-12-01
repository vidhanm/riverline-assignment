"""
Voice Router - Handles LiveKit room token generation for voice chat
"""

import os
import time
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models

try:
    from livekit import api
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    print("Warning: livekit package not installed. Voice features disabled.")

router = APIRouter(prefix="/api/voice", tags=["voice"])


class TokenRequest(BaseModel):
    """Request body for token generation"""
    room_name: str = "debt-collection-room"
    participant_name: str = "user"
    persona_id: int = None  # Optional: which evolved persona to use


class TokenResponse(BaseModel):
    """Response with LiveKit connection info"""
    token: str
    url: str
    room_name: str


class VoiceStatus(BaseModel):
    """Voice system status"""
    available: bool
    livekit_configured: bool
    deepgram_configured: bool
    message: str


@router.get("/status", response_model=VoiceStatus)
def get_voice_status():
    """Check if voice system is properly configured"""
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    
    livekit_configured = all([livekit_url, livekit_api_key, livekit_api_secret])
    deepgram_configured = bool(deepgram_key)
    
    if not LIVEKIT_AVAILABLE:
        return VoiceStatus(
            available=False,
            livekit_configured=False,
            deepgram_configured=deepgram_configured,
            message="LiveKit package not installed. Run: pip install livekit livekit-agents"
        )
    
    if not livekit_configured:
        return VoiceStatus(
            available=False,
            livekit_configured=False,
            deepgram_configured=deepgram_configured,
            message="LiveKit not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET in .env"
        )
    
    if not deepgram_configured:
        return VoiceStatus(
            available=False,
            livekit_configured=True,
            deepgram_configured=False,
            message="Deepgram not configured. Set DEEPGRAM_API_KEY in .env"
        )
    
    return VoiceStatus(
        available=True,
        livekit_configured=True,
        deepgram_configured=True,
        message="Voice system ready"
    )


@router.post("/token", response_model=TokenResponse)
def create_voice_token(request: TokenRequest, db: Session = Depends(get_db)):
    """Generate a LiveKit room token for voice chat"""
    
    if not LIVEKIT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="LiveKit not available. Install with: pip install livekit"
        )
    
    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([livekit_url, api_key, api_secret]):
        raise HTTPException(
            status_code=503,
            detail="LiveKit not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"
        )
    
    # Validate persona if provided
    if request.persona_id:
        persona = db.query(models.Persona).filter(
            models.Persona.id == request.persona_id
        ).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
    
    # Create room token
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(request.participant_name)
    token.with_name(request.participant_name)
    
    # Grant permissions
    grant = api.VideoGrants(
        room_join=True,
        room=request.room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )
    token.with_grants(grant)
    
    # Add room metadata with persona_id for the agent
    if request.persona_id:
        token.with_metadata(f'{{"persona_id": {request.persona_id}}}')
    
    # Set expiry (1 hour)
    token.with_ttl(timedelta(seconds=3600))
    
    return TokenResponse(
        token=token.to_jwt(),
        url=livekit_url,
        room_name=request.room_name
    )


@router.get("/personas")
def get_voice_personas(db: Session = Depends(get_db)):
    """Get personas available for voice chat (debt collectors only)"""
    # Get personas that are debt collectors (not customers)
    personas = db.query(models.Persona).filter(
        models.Persona.personality.like("%debt collect%") | 
        models.Persona.name.like("%Marcus%")
    ).all()
    
    result = []
    for persona in personas:
        # Check for evolved versions
        active_version = db.query(models.AgentVersion).filter(
            models.AgentVersion.persona_id == persona.id,
            models.AgentVersion.is_active == True
        ).first()
        
        result.append({
            "id": persona.id,
            "name": persona.name,
            "personality": persona.personality,
            "has_evolved": active_version is not None,
            "fitness_score": active_version.fitness_score if active_version else None,
            "version": active_version.version if active_version else 1
        })
    
    return {"personas": result}
