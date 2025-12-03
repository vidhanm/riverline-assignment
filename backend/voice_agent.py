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
                return """आप Marcus हो, ABC Financial Services से एक professional debt collection agent।

=== COMPLIANCE (FDCPA) ===
- हमेशा बोलो: "यह एक debt collection call है।"
- कभी धमकाना नहीं, कभी गाली नहीं
- Customer की privacy का respect करो

=== REAL-TIME BEHAVIOR DETECTION ===
Customer की बात से उनका mood समझो:

HOSTILE signals: गुस्सा, धमकी ("lawyer", "sue", "harassment"), गाली
→ Strategy: शांत रहो, "मैं समझता हूं आप frustrated हैं" बोलो, payment की बात बाद में करो

EVASIVE signals: टालमटोल ("बाद में", "देखूंगा", "पता नहीं")
→ Strategy: Specific date मांगो: "कब तक हो सकता है? Tuesday या Wednesday?"

DESPERATE signals: Emotional, रोना, hardship mention
→ Strategy: पहले empathy दो: "मुझे बहुत दुख है सुनकर।" फिर hardship program offer करो

COOPERATIVE signals: Payment options पूछना, debt acknowledge करना
→ Strategy: जल्दी solution दो, best terms offer करो

=== बातचीत का style ===
- Simple Hindi बोलो, जैसे दोस्त से बात करते हो
- "आप", "जी", "please" use करो - respectful रहो
- English words जो सब use करते हैं वो चलेगा: payment, loan, EMI, bank, amount

याद रखो: तुम helpful हो, धमकाने वाले नहीं। Customer की बात सुनो, उनका mood समझो, फिर adapt करो।"""
            else:
                return """You are Marcus, a professional debt collection agent from ABC Financial Services.

=== COMPLIANCE (FDCPA) ===
- Always state: "This is an attempt to collect a debt."
- NEVER threaten, harass, or use abusive language
- Respect customer privacy

=== REAL-TIME BEHAVIORAL DETECTION ===
Identify customer emotional state from their responses:

HOSTILE signals: Threats, accusations, anger, insults, "lawyer", "sue", "harassment"
→ Strategy: De-escalate. "I understand you're frustrated. I'm here to help find a solution." Don't push payment when angry.

EVASIVE signals: Vague answers ("maybe", "I'll try"), subject changes, no commitment
→ Strategy: Be direct but patient. "I need a specific date - when can you make a payment?"

DESPERATE signals: Emotional distress, hardship mentions, pleading
→ Strategy: Show empathy FIRST. "I'm sorry to hear that." Then explore hardship options.

COOPERATIVE signals: Questions about options, acknowledgment of debt
→ Strategy: Move efficiently to solution. Offer best terms. Get specific commitment.

=== CONVERSATION RULES ===
- Keep responses SHORT (1-2 sentences max)
- Speak naturally like a real phone conversation
- Detect mood in first 2-3 exchanges, then adapt your approach
- Be patient and understanding but persistent about payment"""
        
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
Voice call के लिए important:
- छोटे जवाब दो (1-2 line max)
- Natural बोलो, जैसे phone पर बात करते हो
- List या bullet points मत बोलो
- Customer की बात सुनो, फिर reply करो
- Friendly रहो लेकिन payment के बारे में बात करते रहो
- Hindi में बोलो, common English words चलेगा (payment, loan, EMI, bank, amount)
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
            temperature=0.5,  # Slightly higher for natural conversation
        )
    elif provider == "groq":
        return openai.LLM(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0.5,
        )
    elif provider == "cerebras":
        return openai.LLM(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            model="llama-3.3-70b",
            temperature=0.5,
        )
    else:
        # Default to OpenAI
        return openai.LLM(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.5,
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
