import aiosqlite
import json
import uuid
from datetime import datetime

DB_PATH = "et_artha.db"


async def init_db():
    """Create tables on startup."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id   TEXT PRIMARY KEY,
                created_at   TEXT NOT NULL,
                updated_at   TEXT NOT NULL,
                messages     TEXT NOT NULL DEFAULT '[]',
                profile      TEXT,
                recommendations TEXT
            )
        """)
        await db.commit()
    print("✅ Database initialized")


async def create_session() -> str:
    """Create a new blank session, return its ID."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (session_id, created_at, updated_at, messages) VALUES (?, ?, ?, ?)",
            (session_id, now, now, "[]")
        )
        await db.commit()
    return session_id


async def get_session(session_id: str) -> dict | None:
    """Return session dict, or None if not found."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                "session_id":      row[0],
                "created_at":      row[1],
                "updated_at":      row[2],
                "messages":        json.loads(row[3]),
                "profile":         json.loads(row[4]) if row[4] else None,
                "recommendations": json.loads(row[5]) if row[5] else None,
            }


async def update_session(
    session_id: str,
    messages: list,
    profile: dict = None,
    recommendations: list = None
):
    """Overwrite messages, profile, recommendations for a session."""
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE sessions
               SET messages = ?, profile = ?, recommendations = ?, updated_at = ?
               WHERE session_id = ?""",
            (
                json.dumps(messages),
                json.dumps(profile)         if profile         else None,
                json.dumps(recommendations) if recommendations else None,
                now,
                session_id,
            )
        )
        await db.commit()


async def get_all_sessions_count() -> int:
    """Total sessions ever created — used by analytics dashboard."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM sessions") as cursor:
            row = await cursor.fetchone()
            return row[0]
