from fastapi import APIRouter
from ollama_client import check_ollama_running, list_models
from database import get_all_sessions_count

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Returns server status, Ollama status, available models,
    and total session count. Tanaya uses this to confirm backend is live.
    """
    ollama_ok     = await check_ollama_running()
    session_count = await get_all_sessions_count()
    models        = await list_models() if ollama_ok else []

    return {
        "status":           "ok",
        "ollama_running":   ollama_ok,
        "available_models": models,
        "total_sessions":   session_count,
    }
