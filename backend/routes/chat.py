import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database import create_session, get_session, update_session
from ollama_client import generate_stream

router = APIRouter()


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/session/new")
async def new_session():
    """
    Creates a blank session.
    Frontend calls this first, stores the session_id, uses it for all /chat calls.
    """
    session_id = await create_session()
    return {"session_id": session_id}


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint — streams ET Artha's response token by token.

    Flow:
      1. Load session from SQLite
      2. Append user message to history
      3. Build prompt from history
      4. Stream response from Ollama
      5. Save updated session back to SQLite
      6. Send done signal (with profile_ready flag if profile exists)

    ── INTEGRATION NOTE FOR ANUJ ────────────────────────────────────────────
    When Anuj's ConciergeAgent is ready, replace the streaming block below with:

        from agent.concierge import ConciergeAgent
        agent = ConciergeAgent(session)
        result = await agent.process(request.message)

        async def stream_response():
            text = result["response"]
            for i in range(0, len(text), 3):
                chunk = text[i:i+3]
                yield f"data: {json.dumps({'token': chunk, 'done': False})}\\n\\n"
                await asyncio.sleep(0.01)
            await update_session(
                request.session_id,
                messages=result["messages"],
                profile=result.get("profile"),
                recommendations=result.get("recommendations", [])
            )
            yield f"data: {json.dumps({'token': '', 'done': True, 'profile_ready': result.get('profile_complete', False)})}\\n\\n"
    ── END INTEGRATION NOTE ─────────────────────────────────────────────────
    """
    session = await get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Call /api/session/new first.")

    # Add user message to history
    messages = session["messages"]
    messages.append({"role": "user", "content": request.message})

    # Build conversation prompt (last 10 messages for context window)
    history_text = "\n".join([
        f"{'User' if m['role'] == 'user' else 'ET Artha'}: {m['content']}"
        for m in messages[-10:]
    ])
    prompt = f"{history_text}\n\nET Artha:"

    async def stream_response():
        full_response = ""

        async for token in generate_stream(prompt):
            full_response += token
            yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

        # Save assistant reply to session
        messages.append({"role": "assistant", "content": full_response})
        await update_session(request.session_id, messages)

        # Tell frontend streaming is done
        # profile_ready will become True once Anuj's agent sets profile in the session
        profile_ready = session.get("profile") is not None
        yield f"data: {json.dumps({'token': '', 'done': True, 'profile_ready': profile_ready})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",     # prevents nginx from buffering the stream
        },
    )


@router.get("/profile/{session_id}")
async def get_profile(session_id: str):
    """
    Returns the user profile and recommendations for a session.
    Profile is null until Anuj's agent has finished profiling (after ~4-5 turns).
    """
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "profile":         session.get("profile"),
        "recommendations": session.get("recommendations") or [],
    }


@router.post("/profile/{session_id}")
async def save_profile(session_id: str, data: dict):
    """
    Anuj's agent calls this to save a completed profile + recommendations.
    """
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    await update_session(
        session_id,
        session["messages"],
        profile=data.get("profile"),
        recommendations=data.get("recommendations"),
    )
    return {"status": "saved"}
