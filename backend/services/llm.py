import os
from groq import Groq
from cerebras.cloud.sdk import Cerebras
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ===== CONFIGURATION: Change this to switch LLM provider =====
PROVIDER = "nvidia"  # Options: "groq", "cerebras", or "nvidia"
# ==============================================================


def get_llm_response(system_prompt, messages=[], max_tokens=None):
    """Get LLM response from Groq, Cerebras, or NVIDIA"""
    provider = PROVIDER.lower()

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY not set")
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        model = "llama-3.3-70b-versatile"
    elif provider == "cerebras":
        if not os.getenv("CEREBRAS_API_KEY"):
            raise ValueError("CEREBRAS_API_KEY not set")
        client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
        model = "llama-3.3-70b"
    elif provider == "nvidia":
        if not os.getenv("NVIDIA_API_KEY"):
            raise ValueError("NVIDIA_API_KEY not set")
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        model = "meta/llama-3.3-70b-instruct"
    else:
        raise ValueError(f"Invalid PROVIDER: {provider}. Use 'groq', 'cerebras', or 'nvidia'")

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    # Build parameters
    params = {
        "model": model,
        "messages": full_messages
    }
    if max_tokens:
        params["max_tokens"] = max_tokens

    response = client.chat.completions.create(**params)

    return response.choices[0].message.content
