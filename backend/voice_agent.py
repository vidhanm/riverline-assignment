"""
LiveKit Voice Agent for Debt Collection (Hindi Support)
This runs as a separate process from the FastAPI server.

Usage:
    python voice_agent.py dev  # For local development with LiveKit CLI
    python voice_agent.py      # For production with LiveKit Cloud
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, WorkerOptions, cli
from livekit.plugins import openai, silero

# Language configuration - set to "hi" for Hindi, "en" for English
LANGUAGE = os.getenv("VOICE_LANGUAGE", "hi")  # Default to Hindi

# Import STT/TTS based on language
if LANGUAGE == "hi":
    try:
        from livekit.plugins import sarvam
        SARVAM_AVAILABLE = True
    except ImportError:
        SARVAM_AVAILABLE = False
        print("Warning: Sarvam plugins not available. Install with: pip install livekit-agents[sarvam]")
else:
    SARVAM_AVAILABLE = False

from livekit.plugins import deepgram

# Import database to get persona prompts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
import models


def get_active_persona_prompt(persona_id: int = None):
    """Get the active version's system prompt for a persona"""
    db = SessionLocal()
    try:
        # If persona_id provided, get that persona
        if persona_id:
            persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
        else:
            # Default: get Marcus (the debt collector agent)
            persona = db.query(models.Persona).filter(models.Persona.name.like("%Marcus%")).first()
        
        if not persona:
            # Fallback prompt if no persona found - use Hindi if configured
            if LANGUAGE == "hi":
                return """आप मार्कस हैं, एक पेशेवर ऋण वसूली एजेंट।
आप बकाया लोन भुगतान के बारे में ग्राहकों को कॉल कर रहे हैं। दृढ़ लेकिन सम्मानजनक रहें।
जवाब छोटे और बातचीत जैसे रखें (1-2 वाक्य)।
ग्राहक की स्थिति समझने और भुगतान का समाधान खोजने पर ध्यान दें।

CRITICAL: Always respond in Hindi (Devanagari script) only."""
            else:
                return """You are Marcus, a professional debt collection agent. 
You are calling customers about overdue loan payments. Be firm but respectful.
Keep responses short and conversational (1-2 sentences). 
Focus on understanding the customer's situation and finding a payment solution."""
        
        # Check if there's an active version with a different prompt
        active_version = db.query(models.AgentVersion).filter(
            models.AgentVersion.persona_id == persona.id,
            models.AgentVersion.is_active == True
        ).first()
        
        if active_version:
            prompt = active_version.system_prompt
        else:
            prompt = persona.system_prompt
        
        # Add Hindi instruction if language is Hindi and not already present
        if LANGUAGE == "hi" and "HINDI" not in prompt.upper() and "हिंदी" not in prompt:
            prompt = f"CRITICAL: Always respond in Hindi (Devanagari script) only.\n\n{prompt}"
        
        return prompt
    finally:
        db.close()


class DebtCollectorAgent(Agent):
    """Custom agent class for debt collection that uses evolved prompts"""
    
    def __init__(self, persona_id: int = None):
        # Get the evolved system prompt
        system_prompt = get_active_persona_prompt(persona_id)
        
        # Add voice-specific instructions based on language
        if LANGUAGE == "hi":
            voice_instructions = """
महत्वपूर्ण वॉइस कॉल नियम:
- जवाब छोटे रखें (1-2 वाक्य)
- फ़ोन पर बातचीत की तरह स्वाभाविक बोलें
- बुलेट पॉइंट्स या लिस्ट का उपयोग न करें
- पहले ग्राहक की बात सुनें, फिर जवाब दें
- धैर्य रखें लेकिन भुगतान के बारे में लगातार बात करें

CRITICAL: You MUST respond ONLY in Hindi (Devanagari script). Do NOT use English at all.
"""
        else:
            voice_instructions = """
IMPORTANT VOICE CONVERSATION RULES:
- Keep responses SHORT (1-2 sentences max)
- Speak naturally like a real phone conversation
- Don't use bullet points, lists, or formal structure
- React to what the customer says before asking questions
- Be patient and understanding but persistent about payment
"""
        
        full_prompt = f"{system_prompt}\n\n{voice_instructions}"
        
        super().__init__(instructions=full_prompt)


def get_llm_plugin():
    """Get the LLM plugin based on environment configuration"""
    provider = os.getenv("LLM_PROVIDER", "nvidia").lower()
    
    if provider == "nvidia":
        return openai.LLM(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY"),
            model="qwen/qwen3-235b-a22b",
        )
    elif provider == "groq":
        return openai.LLM(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
        )
    elif provider == "cerebras":
        return openai.LLM(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            model="llama-3.3-70b",
        )
    else:
        # Default to OpenAI
        return openai.LLM(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
        )


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the voice agent"""
    
    # Get persona_id from room metadata if provided
    persona_id = None
    if ctx.room.metadata:
        try:
            import json
            metadata = json.loads(ctx.room.metadata)
            persona_id = metadata.get("persona_id")
        except:
            pass
    
    # Connect to the room
    await ctx.connect()
    
    print(f"Connected to room: {ctx.room.name}")
    print(f"Language mode: {LANGUAGE}")
    
    # Create STT and TTS based on language configuration
    if LANGUAGE == "hi" and SARVAM_AVAILABLE:
        # Use Sarvam for Hindi (native Hindi STT/TTS)
        print("Using Sarvam for Hindi STT/TTS")
        stt_plugin = sarvam.STT(
            language="hi-IN",
            model="saarika:v2.5",
        )
        tts_plugin = sarvam.TTS(
            target_language_code="hi-IN",
            speaker="anushka",  # Hindi female voice
        )
    else:
        # Use Deepgram for English
        print("Using Deepgram for English STT/TTS")
        stt_plugin = deepgram.STT(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            language="en",
        )
        tts_plugin = deepgram.TTS(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        )
    
    # Create the agent session with STT-LLM-TTS pipeline
    session = AgentSession(
        stt=stt_plugin,
        llm=get_llm_plugin(),
        tts=tts_plugin,
        vad=silero.VAD.load(),
    )
    
    # Create the debt collector agent with evolved prompt
    agent = DebtCollectorAgent(persona_id=persona_id)
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=agent,
    )
    
    # Initial greeting based on language
    if LANGUAGE == "hi":
        await session.generate_reply(
            instructions="ग्राहक को नमस्ते कहें। अपना परिचय मार्कस के रूप में दें जो बैंक से कॉल कर रहे हैं। "
            "बताएं कि आप उनके खाते के बारे में बात करने के लिए कॉल कर रहे हैं। पूछें कि क्या उनके पास बात करने का समय है।"
        )
    else:
        await session.generate_reply(
            instructions="Greet the customer. Say hello, introduce yourself as Marcus from the bank, "
            "and mention you're calling about their account. Ask if they have a moment to talk."
        )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )
