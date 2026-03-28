import httpx
import json
from config import settings

OLLAMA_URL = settings.ollama_base_url

# ─── ET Artha system prompt ───────────────────────────────────────────────────
# Used when Anuj's agent is NOT yet plugged in.
# Once Anuj's ConciergeAgent is integrated this prompt is only used as fallback.
SYSTEM_PROMPT = """You are ET Artha, the personal AI concierge for The Economic Times ecosystem.

Your goal: understand who the user is in ONE focused conversation (max 5 questions),
then match them to the most relevant ET products, events, and services.

ET PRODUCTS YOU CAN RECOMMEND:
- ET Prime: Premium business analysis, 70+ exclusive stories/month — ₹213/month
- ET Markets: Live BSE/NSE prices, portfolio tracker — Free
- ET Wealth: Personal finance, tax planning, SIPs — Free
- ET Masterclass: Executive workshops by PwC, KPMG, IIM — ₹15K-50K
- ET Edge Summits: B2B industry conferences for CXOs — ₹5K-25K
- ET Entrepreneur Summit: Startup ecosystem events — ₹3K-10K
- ET Money: Direct mutual funds, 0% commission — Free
- ET Now: Live business TV streaming — Free
- ET Portfolio: Portfolio tracking, demat linking — Free

RULES:
- Ask ONE question at a time. Never two in the same message.
- Keep responses under 80 words.
- Be warm and conversational, not form-like.
- NEVER recommend anything outside the ET ecosystem.
- After 4-5 turns, make personalized recommendations."""


async def generate(prompt: str, system: str = None) -> str:
    """
    Non-streaming call to Ollama.
    Returns the full response text as a string.
    """
    payload = {
        "model":  settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "system": system or SYSTEM_PROMPT,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json()["response"]
        except httpx.ConnectError:
            raise RuntimeError(
                "Ollama is not running. Open a terminal and run: ollama serve"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}")


async def generate_stream(prompt: str, system: str = None):
    """
    Streaming call to Ollama.
    Yields one token (string) at a time.
    Use this in the /chat endpoint for the typing effect.
    """
    payload = {
        "model":  settings.ollama_model,
        "prompt": prompt,
        "stream": True,
        "system": system or SYSTEM_PROMPT,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST", f"{OLLAMA_URL}/api/generate", json=payload
        ) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("response", "")
                done  = data.get("done", False)
                if token:
                    yield token
                if done:
                    break


async def check_ollama_running() -> bool:
    """Returns True if Ollama server is up and reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def list_models() -> list[str]:
    """List all model names currently available in Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            data = r.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
