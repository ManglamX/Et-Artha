from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routes.chat import router as chat_router
from routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────
    print("🚀 Starting ET Artha backend...")
    await init_db()
    print(f"🤖 Model: {settings.ollama_model}")
    print(f"🌐 Ollama: {settings.ollama_base_url}")
    print("📖 API docs: http://localhost:8000/docs")
    yield
    # ── Shutdown ──────────────────────────────
    print("👋 ET Artha backend stopped.")


app = FastAPI(
    title="ET Artha API",
    version=settings.app_version,
    description="AI Concierge backend for Economic Times Ecosystem",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allows Tanaya's frontend (localhost:3000 or Vercel) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        settings.frontend_url,
        "https://*.vercel.app",   # Tanaya's deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(chat_router,   prefix="/api", tags=["Chat"])
app.include_router(health_router, prefix="/api", tags=["Health"])


@app.get("/")
async def root():
    return {
        "project": "ET Artha",
        "status":  "running",
        "docs":    "/docs",
        "health":  "/api/health",
    }
