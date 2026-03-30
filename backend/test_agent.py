# backend/test_agent.py
# Standalone test — run without Manglam's FastAPI server
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.concierge import ConciergeAgent


async def test():
    fake_session = {
        "session_id": "test-123",
        "messages": [],
        "profile": None,
        "recommendations": []
    }
    agent = ConciergeAgent(fake_session)
    result = await agent.process("Hi, I am a software engineer")
    print("Response:", result["response"])
    print("Profile:", result["profile"])
    print("Recommendations:", result["recommendations"])


if __name__ == "__main__":
    asyncio.run(test())
