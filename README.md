# ET Artha — AI Concierge for The Economic Times

> **Hackathon Project · Economic Times · Built in 72 hours**

ET Artha is an AI-powered conversational concierge that profiles ET users in ~5 turns and recommends the most relevant products from The Economic Times ecosystem — ET Prime, ET Markets, ET Wealth, ET Money, ET Masterclass, ET Edge Summits, and more.

---

## 🎯 What It Does

1. User opens the chat at `localhost:3000`
2. ET Artha asks 4–5 focused questions to understand who the user is
3. The LangGraph agent profiles the user into one of 6 archetypes
4. A personalized profile card + product recommendations appear in real time
5. Cross-sell triggers fire automatically based on keywords (e.g. "startup" → ET Entrepreneur Summit)

### 6 User Archetypes
| Archetype | Who They Are |
|---|---|
| 📈 THE MARKET MAVERICK | Active trader, checks Nifty/Sensex daily |
| 🌱 THE WEALTH BUILDER | SIP investor, goal-based, long-term wealth |
| 🏢 THE CORNER OFFICE | CXO/senior exec, policy & global macro |
| 🚀 THE STARTUP SHERPA | Founder/investor, startup ecosystem |
| 🛡️ THE CAREFUL PLANNER | Conservative, FD/insurance focused |
| 📚 THE CURIOUS LEARNER | Student/first-time investor |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│        Next.js Frontend             │
│        localhost:3000               │
│  ChatInterface · ProfileCard        │
│  RecommendationPanel · VoiceButton  │
└────────────────┬────────────────────┘
                 │ HTTP / SSE
┌────────────────▼────────────────────┐
│        FastAPI Backend              │
│        localhost:8000               │
│  POST /api/session/new              │
│  POST /api/chat  (SSE stream)       │
│  GET  /api/profile/{session_id}     │
└──────┬──────────────────┬───────────┘
       │                  │
┌──────▼──────┐   ┌───────▼────────┐
│ LangGraph   │   │  Ollama        │
│ Concierge   │   │  et-artha      │
│ Agent       │   │  (Llama 3.2 3B │
│ + ChromaDB  │   │  fine-tuned)   │
└─────────────┘   └────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, TypeScript, Framer Motion |
| Backend | FastAPI, Python 3.12, aiosqlite |
| AI Agent | LangGraph, ChromaDB, sentence-transformers |
| LLM | Llama 3.2 3B (fine-tuned with Unsloth), served via Ollama |
| Database | SQLite (session storage) |
| Vector DB | ChromaDB (ET product knowledge base) |

---

## 📁 Project Structure

```
et-artha/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (env vars)
│   ├── database.py              # SQLite session storage
│   ├── ollama_client.py         # Ollama HTTP client + fallback
│   ├── recommender.py           # Rule-based recommendation engine
│   ├── archetype.py             # Archetype classifier
│   ├── Modelfile                # Ollama model config for et-artha
│   ├── requirements.txt
│   ├── .env                     # Local config (never commit)
│   ├── agent/
│   │   ├── concierge.py         # LangGraph ConciergeAgent
│   │   ├── profiler.py          # Profile extraction helpers
│   │   ├── triggers.py          # Cross-sell keyword triggers
│   │   └── prompts.py           # System prompts
│   ├── knowledge/
│   │   ├── loader.py            # Loads ET products into ChromaDB
│   │   ├── retriever.py         # Semantic product retrieval
│   │   ├── et_products.json     # ET product catalog
│   │   ├── et_events.json       # ET events catalog
│   │   └── et_services.json     # ET services catalog
│   ├── data/
│   │   ├── training_data.json   # Fine-tuning dataset (300 examples)
│   │   └── demo_personas.json   # Demo user scripts for hackathon
│   └── routes/
│       ├── chat.py              # /api/chat, /api/session/new
│       ├── profile.py           # /api/profile/{session_id}
│       └── health.py            # /api/health
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Main chat page
│       │   ├── layout.tsx
│       │   ├── globals.css
│       │   └── analytics/       # Impact dashboard page
│       ├── components/
│       │   ├── ChatInterface.tsx
│       │   ├── MessageBubble.tsx
│       │   ├── ProfileCard.tsx
│       │   ├── RecommendationPanel.tsx
│       │   └── VoiceButton.tsx
│       └── lib/
│           ├── api.ts           # Backend API calls (SSE streaming)
│           └── types.ts         # TypeScript types
├── colab/
│   └── fine_tune_et_artha.py   # Llama 3.2 3B fine-tuning script
├── data/
│   └── seed_data.json          # Original seed dataset
└── INTEGRATION.md              # Team integration guide
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running
- `et-artha` model loaded (see below)

### 1. Load the `et-artha` Ollama Model
```bash
cd backend
ollama create et-artha -f Modelfile
ollama list   # verify et-artha:latest appears
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Configure environment
cp .env.example .env           # edit as needed

# Start the server
uvicorn main:app --reload --port 8000
```
API docs available at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
App available at: `http://localhost:3000`

### 4. Load Knowledge Base (first time only)
```bash
cd backend
venv\Scripts\activate
python -c "from knowledge.loader import load_knowledge_base; load_knowledge_base()"
# Output: ✅ Loaded 13 items into ChromaDB
```

---

## 🔌 API Reference

### `POST /api/session/new`
Creates a new conversation session.
```json
// Response
{ "session_id": "uuid-string" }
```

### `POST /api/chat`
Streams ET Artha's response token by token (Server-Sent Events).
```json
// Request
{ "session_id": "uuid", "message": "Hi I'm a software engineer" }

// SSE stream events
data: {"token": "Hello", "done": false}
data: {"token": " there", "done": false}
data: {"token": "", "done": true, "profile_ready": false}
```

### `GET /api/profile/{session_id}`
Returns the extracted user profile and recommendations (available after ~4 turns).
```json
{
  "profile": {
    "archetype": "THE WEALTH BUILDER",
    "profession": "Software Engineer",
    "experience": "beginner",
    "goal": "Save for a house in 5 years",
    "interests": ["SIP", "mutual funds", "tax saving"]
  },
  "recommendations": [
    {
      "product": "ET Wealth",
      "reason": "Best beginner guides on SIPs and goal-based investing",
      "cta": "Plan your finances free",
      "url": "https://economictimes.indiatimes.com/wealth",
      "priority": 1,
      "category": "finance"
    }
  ]
}
```

---

## 🧪 Test Scenarios

### Scenario 1: Riya — The Wealth Builder
```
"Hi! I'm Riya. I'm a software engineer, just started my first SIP."
"I want to save for a house in 5 years and retire comfortably."
"I'm pretty new. This is my first investment ever."
"I prefer reading articles. I can spend 15 minutes a day."
→ Profile: THE WEALTH BUILDER
→ Recs: ET Wealth, ET Money, ET Prime
```

### Scenario 2: Vikram — The Corner Office
```
"I'm Vikram, CFO at a manufacturing company."
"I follow macro trends, RBI policy, and M&A news closely."
"I attend 2-3 industry conferences per year."
→ Profile: THE CORNER OFFICE
→ Recs: ET Prime, ET Masterclass, ET Edge
```

### Scenario 3: Cross-Sell Trigger
```
"I'm building a startup, just closed our seed round."
→ ET Artha proactively mentions ET Entrepreneur Summit
```

---

## 🤖 AI Model

The `et-artha` model is **Llama 3.2 3B Instruct** fine-tuned with:
- **300 training examples** of ET Artha persona conversations
- **Unsloth** for 4× faster training on Google Colab T4 GPU
- **Q4_K_M quantization** → ~2GB GGUF file served via Ollama

The LangGraph `ConciergeAgent` orchestrates:
1. **Respond node** — generates contextual replies with cross-sell triggers
2. **Extract Profile node** — runs after 4 turns to extract structured JSON profile
3. **Recommend node** — queries ChromaDB for RAG-based product recommendations

---

## 🚢 Deployment (Demo Day)

```bash
# On demo laptop:
ollama serve                           # keep model running
uvicorn main:app --host 0.0.0.0 --port 8000

# Expose backend to internet:
ngrok http 8000
# → copy https://xxx.ngrok.io URL

# Frontend (Vercel):
# Set NEXT_PUBLIC_BACKEND_URL = https://xxx.ngrok.io
# Deploy: npx vercel --prod
```

---

## 👥 Team

| Member | Responsibility |
|---|---|
| Manglam | FastAPI backend, Ollama serving, SQLite session storage, CORS |
| Tanaya | Next.js frontend, chat UI, voice input, profile card animations |
| Anuj | LangGraph agent, ChromaDB knowledge base, training data generation |
| Latika | Llama 3.2 3B fine-tuning, recommendation engine, archetype classifier |

---

*Built for the Economic Times Hackathon · March 2026*
