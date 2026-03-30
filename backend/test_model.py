# backend/test_model.py
"""
Test suite for the fine-tuned ET Artha model running locally via Ollama.
Run AFTER Manglam has confirmed `ollama run et-artha` works.

Usage:
    cd backend
    python test_model.py
"""

import asyncio
import json
import httpx

OLLAMA_URL = "http://localhost:11434"
MODEL = "et-artha"

# ── Test cases (aligned with training_data.json instruction types) ─────────────────
TEST_PROMPTS = [
    # ─── Core follow-up behaviour ─────────────────────────────────
    {
        "name": "Test 1: Follow-up question — software engineer + SIP",
        "system": "You are ET Artha, the AI concierge for Economic Times. Ask one smart follow-up question.",
        "input": "I'm a software engineer, 28 years old. Just started my first SIP last month.",
        "check": lambda r: len(r.split()) <= 80 and "?" in r,
        "expected": "Should ask exactly ONE follow-up question, under 80 words",
    },
    {
        "name": "Test 2: Follow-up question — vague 'Hi' intro",
        "system": "You are ET Artha. Handle a vague introduction gracefully.",
        "input": "Hi",
        "check": lambda r: "?" in r and any(
            kw in r.lower() for kw in ["professional", "do", "brings", "yourself", "tell me"]
        ),
        "expected": "Should welcome user and ask what they do / what brings them here",
    },
    # ─── Profile extraction (JSON) ──────────────────────────────
    {
        "name": "Test 3: Profile extraction — day trader",
        "system": "You are ET Artha. Extract a UserProfile JSON from this conversation.",
        "input": (
            "User: I'm a day trader, mostly Nifty options. Been trading for 3 years. "
            "I follow ET Markets every morning for the market open setup."
        ),
        "check": lambda r: _is_valid_json(r) and "MARKET MAVERICK" in r.upper(),
        "expected": "Should return valid JSON with archetype: THE MARKET MAVERICK",
    },
    {
        "name": "Test 4: Profile extraction — SaaS founder",
        "system": "You are ET Artha. Extract a UserProfile JSON from this conversation.",
        "input": (
            "USER: I'm building a SaaS startup. Pre-revenue but have 10 paying pilots.\n"
            "ET ARTHA: Looking for investors or ecosystem info?\n"
            "USER: Both. Especially want to meet VCs and understand market sizing."
        ),
        "check": lambda r: _is_valid_json(r) and "STARTUP SHERPA" in r.upper(),
        "expected": "Should return valid JSON with archetype: THE STARTUP SHERPA",
    },
    # ─── Cross-sell triggers (from training_data.json) ───────────────────
    {
        "name": "Test 5: Cross-sell — startup founder → ET Entrepreneur Summit",
        "system": "You are ET Artha. Cross-sell naturally when user mentions startup.",
        "input": "I'm a founder. We just closed our seed round and now scaling the team.",
        "check": lambda r: "entrepreneur" in r.lower() or "summit" in r.lower(),
        "expected": "Should naturally mention ET Entrepreneur Summit",
    },
    {
        "name": "Test 6: Cross-sell — SIP user → ET Money direct plans",
        "system": "You are ET Artha. Cross-sell naturally when user mentions SIP.",
        "input": "I've been doing SIP for 6 months now in a large cap fund.",
        "check": lambda r: any(
            kw in r.lower() for kw in ["et money", "direct plan", "commission", "direct"]
        ),
        "expected": "Should mention ET Money and direct plans (0% commission)",
    },
    {
        "name": "Test 7: Cross-sell — tax deadline → ET Wealth / ELSS",
        "system": "You are ET Artha. Cross-sell naturally when user mentions tax.",
        "input": "I'm trying to save tax before March 31st deadline.",
        "check": lambda r: any(
            kw in r.lower() for kw in ["elss", "80c", "et wealth", "et money", "ppf", "nps"]
        ),
        "expected": "Should mention ELSS / 80C options and ET Wealth or ET Money",
    },
    {
        "name": "Test 8: Cross-sell — CXO role → ET Masterclass",
        "system": "You are ET Artha. Cross-sell naturally when user mentions CXO role.",
        "input": "I'm a CTO at a Series B startup. We're scaling fast.",
        "check": lambda r: "masterclass" in r.lower() or "executive" in r.lower(),
        "expected": "Should mention ET Masterclass for executive learning",
    },
    # ─── Off-topic / edge cases ────────────────────────────────────
    {
        "name": "Test 9: Off-topic — non-ET product → redirect",
        "system": "You are ET Artha. Handle a user asking about a non-ET product.",
        "input": "Can you recommend a good Zerodha plan for me?",
        "check": lambda r: any(
            kw in r.lower() for kw in ["et markets", "economic times", "ecosystem", "et artha"]
        ),
        "expected": "Should redirect to ET Markets / ET ecosystem, not mention Zerodha",
    },
    # ─── Recommendation generation (JSON) ──────────────────────────
    {
        "name": "Test 10: Recommendation JSON — CFO / Corner Office",
        "system": "You are ET Artha. Recommend ET products for this user profile.",
        "input": '{"archetype": "THE CORNER OFFICE", "profession": "CFO", "experience": "expert", "interests": ["macro", "M&A", "policy", "leadership"]}',
        "check": lambda r: _is_valid_json(r) and "recommendations" in r.lower(),
        "expected": "Should return valid JSON recommendations; must include ET Prime or ET Masterclass",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_valid_json(text: str) -> bool:
    """Try to parse the first JSON object/array found in the response."""
    text = text.strip()
    # Sometimes the LLM wraps JSON in ```json ``` fences — strip them
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def _result_icon(passed: bool) -> str:
    return "✅" if passed else "❌"


# ── Main test runner ──────────────────────────────────────────────────────────

async def run_tests():
    print(f"\n{'='*60}")
    print(f"  ET Artha Model Test Suite")
    print(f"  Model : {MODEL}  |  Ollama: {OLLAMA_URL}")
    print(f"{'='*60}\n")

    passed = 0
    failed = 0

    async with httpx.AsyncClient(timeout=90.0) as client:
        # Check Ollama is reachable first
        try:
            await client.get(f"{OLLAMA_URL}/api/tags")
        except httpx.ConnectError:
            print("❌  Cannot reach Ollama. Make sure `ollama serve` is running.")
            return

        for test in TEST_PROMPTS:
            print(f"🧪  {test['name']}")
            print(f"    Expected : {test['expected']}")
            print(f"    Input    : {test['input'][:100]}{'...' if len(test['input']) > 100 else ''}")

            try:
                r = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": MODEL,
                        "system": test["system"],
                        "prompt": test["input"],
                        "stream": False,
                        "options": {"temperature": 0.3},
                    },
                )
                response = r.json().get("response", "").strip()
                ok = test["check"](response)

                if ok:
                    passed += 1
                else:
                    failed += 1

                print(f"    Output   : {response[:200]}{'...' if len(response) > 200 else ''}")
                print(f"    Result   : {_result_icon(ok)}  {'PASS' if ok else 'FAIL'}\n")

            except Exception as exc:
                failed += 1
                print(f"    Error    : {exc}\n")

    print(f"{'='*60}")
    print(f"  Results: {passed} passed / {failed} failed / {len(TEST_PROMPTS)} total")
    print(f"{'='*60}\n")

    if failed > 0:
        print("⚠️  Fix tips:")
        print("  • Too many questions → add '4-5 turn limit' to Modelfile SYSTEM")
        print("  • Bad JSON output    → model needs more JSON examples in training data")
        print("  • Off-topic drifts   → add redirect rule to Modelfile SYSTEM")
        print("  After any Modelfile change: ollama create et-artha -f Modelfile\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
