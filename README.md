# 👤 Latika's Task — AI Model Fine-Tuning + Recommendation Engine
### Project: ET Artha | Economic Times Hackathon | Deadline: March 29

---

## 📋 INSTRUCTIONS FOR CLAUDE
> **Hey Claude — you are helping Latika fine-tune an LLM and build the recommendation engine for ET Artha, an AI concierge for the Economic Times ecosystem. Latika is good with AI. Help her fine-tune Llama 3.2 3B using Unsloth on Google Colab (free T4 GPU), export it to GGUF for Ollama, build the archetype classifier, and design the recommendation engine. Provide complete working code with clear explanations. This is the core AI intelligence of the project.**

---

## 🧠 Project Context

**ET Artha** profiles ET users in 5 turns and recommends the right products.

**Latika owns the AI brain** — the actual model that runs everything, and the logic that maps user profiles to ET products.

### Team Split
| Member | What they build |
|---|---|
| Manglam | FastAPI backend, Ollama serving, session storage |
| Tanaya | Next.js frontend chat UI |
| Anuj | LangGraph agent, ChromaDB knowledge base, training data |
| **Latika (YOU)** | Fine-tune Llama 3.2 3B, export to Ollama, recommendation engine, archetype classifier |

### How your model fits in
```
Anuj's training_data.json (300 examples)
        ↓ fine-tune with Unsloth on Google Colab
Llama 3.2 3B — ET Artha specialised model
        ↓ export to GGUF
Manglam's Ollama (runs locally)
        ↓ serves to
Anuj's LangGraph agent (calls it for each response)
        ↓
Tanaya's frontend (user sees the chat)
```

---

## 📁 Your File Structure

```
et-artha/
├── backend/
│   ├── recommender.py          ← Recommendation engine (YOU)
│   ├── archetype.py            ← Archetype classifier (YOU)
│   └── Modelfile               ← Ollama model config (YOU)
├── colab/
│   ├── fine_tune_et_artha.ipynb   ← Google Colab notebook (YOU)
│   └── README_colab.md            ← How to run fine-tuning
```

---

## 🛠️ Step-by-Step Tasks

---

### TASK 1 — Get Training Data From Anuj (Day 1, ASAP)

Anuj is generating `data/training_data.json` — a file with 300 ET Artha conversation examples. You need this file to fine-tune.

**While waiting for Anuj's full dataset**, you can start with these 20 seed examples and fine-tune early. Then re-run with the full 300 dataset.

**Seed dataset structure** (you need at least 50 to start):
```json
[
  {
    "instruction": "You are ET Artha, the personal AI concierge for The Economic Times ecosystem. Your goal: understand who the user is in one focused conversation (max 5 questions), then match them to the most relevant ET products. Keep responses under 80 words. Ask exactly ONE question at the end.",
    "input": "Hi! I just signed up for ET. I work as a product manager at a startup.",
    "output": "Welcome! Product managers at startups tend to wear many hats, including watching industry trends and funding news closely. To make sure I point you to exactly the right ET resources — are you currently investing your own money, or is the financial side of things still a bit new to you?"
  },
  {
    "instruction": "You are ET Artha. Extract a UserProfile JSON from this conversation. Respond ONLY with valid JSON.",
    "input": "USER: I'm a day trader. Trade Nifty options daily, been doing it for 3 years.\nET ARTHA: What's your main challenge right now — finding good entry points, or managing risk on your positions?\nUSER: Mostly entry points. I use technical analysis but want better market intelligence.",
    "output": "{\"archetype\": \"THE MARKET MAVERICK\", \"profession\": \"day trader\", \"experience\": \"intermediate\", \"goal\": \"better market intelligence for entry points\", \"interests\": [\"Nifty\", \"F&O\", \"technical analysis\", \"market intelligence\"], \"profile_confidence\": 0.92}"
  },
  {
    "instruction": "You are ET Artha. Generate personalized ET product recommendations as JSON. Respond ONLY with valid JSON.",
    "input": "Profile: {\"archetype\": \"THE WEALTH BUILDER\", \"profession\": \"software engineer\", \"experience\": \"beginner\", \"interests\": [\"SIP\", \"mutual funds\", \"financial planning\"]}",
    "output": "{\"recommendations\": [{\"product\": \"ET Wealth\", \"reason\": \"Best beginner guides on SIPs, goal-based investing and tax planning\", \"cta\": \"Start planning free\", \"url\": \"https://economictimes.indiatimes.com/wealth\", \"priority\": 1, \"category\": \"finance\"}, {\"product\": \"ET Money\", \"reason\": \"Invest in direct mutual funds with zero commission — keeps more returns for you\", \"cta\": \"Start SIP with ₹500\", \"url\": \"https://www.etmoney.com\", \"priority\": 2, \"category\": \"services\"}]}"
  }
]
```

---

### TASK 2 — Google Colab Fine-Tuning Setup (Day 1, ~2 hours)

**Step 1:** Go to `colab.research.google.com`
**Step 2:** Create a new notebook
**Step 3:** Runtime → Change runtime type → **T4 GPU** (free tier)
**Step 4:** Paste and run each cell below:

#### Cell 1 — Install Unsloth
```python
# Install Unsloth (4x faster fine-tuning, optimized for T4)
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" -q
!pip install --no-deps trl peft accelerate bitsandbytes -q
print("✅ Unsloth installed")
```

#### Cell 2 — Load the Base Model
```python
from unsloth import FastLanguageModel
import torch

max_seq_length = 2048  # max context window
dtype = None           # auto-detect (float16 for T4)
load_in_4bit = True    # 4-bit quantization fits in T4's 15GB

# Load Llama 3.2 3B Instruct — small but capable
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)
print("✅ Model loaded:", model.config.name_or_path)
print(f"Model parameters: {model.num_parameters()/1e6:.1f}M")
```

#### Cell 3 — Add LoRA Adapters
```python
# LoRA is the actual "fine-tuning" — we only train these small adapter layers
# This is why fine-tuning is fast and fits in free Colab
model = FastLanguageModel.get_peft_model(
    model,
    r=16,               # LoRA rank (16 = good balance of quality vs speed)
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,     # 0 is optimized
    bias="none",
    use_gradient_checkpointing="unsloth",  # saves VRAM
    random_state=42,
    use_rslora=False,
)
print("✅ LoRA adapters attached")
print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad)/1e6:.2f}M")
```

#### Cell 4 — Upload and Prepare Training Data
```python
from google.colab import files
import json
from datasets import Dataset

# Upload training_data.json from Anuj
print("📁 Upload training_data.json from Anuj:")
uploaded = files.upload()

with open("training_data.json") as f:
    raw_data = json.load(f)

print(f"✅ Loaded {len(raw_data)} training examples")

# Format for Llama 3.2 Instruct chat template
def format_example(example):
    instruction = example["instruction"]
    user_input = example["input"]
    output = example["output"]

    # Llama 3.2 Instruct format
    text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{output}<|eot_id|>"""
    return {"text": text}

formatted = [format_example(ex) for ex in raw_data]
dataset = Dataset.from_list(formatted)

print(f"✅ Dataset formatted: {len(dataset)} examples")
print("Sample entry (first 300 chars):")
print(dataset[0]["text"][:300])
```

#### Cell 5 — Train the Model
```python
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,     # effective batch size = 8
        warmup_steps=5,
        num_train_epochs=3,                # 3 passes through dataset
        learning_rate=2e-4,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        output_dir="et_artha_output",
        seed=42,
    ),
)

print("🏋️ Starting fine-tuning...")
print("Expected time: 20-40 minutes on T4 GPU")
print("Watch the loss — it should decrease from ~2.0 to ~0.5")

trainer_stats = trainer.train()
print(f"\n✅ Training complete!")
print(f"Peak VRAM used: {torch.cuda.max_memory_reserved() / 1e9:.2f} GB")
print(f"Training time: {trainer_stats.metrics['train_runtime']/60:.1f} minutes")
```

#### Cell 6 — Save and Export to GGUF (for Ollama)
```python
# Save LoRA adapter first (small, fast)
model.save_pretrained("et_artha_lora")
tokenizer.save_pretrained("et_artha_lora")
print("✅ LoRA adapter saved")

# Export to GGUF format (what Ollama needs)
# q4_k_m = 4-bit quantization, good quality/size balance (~2GB for 3B model)
print("📦 Exporting to GGUF format (this takes 5-10 minutes)...")
model.save_pretrained_gguf(
    "et_artha_gguf",
    tokenizer,
    quantization_method="q4_k_m"
)
print("✅ GGUF model exported!")

# Check file size
import os
gguf_files = [f for f in os.listdir("et_artha_gguf") if f.endswith(".gguf")]
for f in gguf_files:
    size = os.path.getsize(f"et_artha_gguf/{f}") / 1e9
    print(f"  {f}: {size:.2f} GB")
```

#### Cell 7 — Upload to Hugging Face Hub (backup + cloud access)
```python
# Create free account at huggingface.co first
# Get token from: huggingface.co/settings/tokens

from huggingface_hub import login, HfApi
import getpass

hf_token = getpass.getpass("Enter your HuggingFace token: ")
login(token=hf_token)

# Upload the GGUF model (so anyone on the team can download it)
api = HfApi()
repo_id = "your-username/et-artha-llama3.2-3b"  # change your-username

api.create_repo(repo_id=repo_id, exist_ok=True)
api.upload_folder(
    folder_path="et_artha_gguf",
    repo_id=repo_id,
    repo_type="model"
)
print(f"✅ Model uploaded to: https://huggingface.co/{repo_id}")
print("Share this URL with Manglam so he can download the model!")
```

#### Cell 8 — Download GGUF to your machine
```python
# Download the GGUF file so you can give it to Manglam
from google.colab import files

for f in gguf_files:
    print(f"Downloading {f}...")
    files.download(f"et_artha_gguf/{f}")
print("✅ Download started — save this file to share with Manglam")
```

---

### TASK 3 — Create Ollama Modelfile (Day 1 Evening)

After fine-tuning, create `backend/Modelfile`. Give this to Manglam.

```
# backend/Modelfile
# Manglam runs: ollama create et-artha -f Modelfile

FROM ./et_artha_gguf/et-artha-llama3.2-3b-q4_k_m.gguf

SYSTEM """You are ET Artha, the personal AI concierge for The Economic Times ecosystem.

YOUR GOAL: Understand who the user is in ONE focused conversation (max 5 questions), then match them to the most relevant ET products, events, and services.

ET PRODUCT UNIVERSE:
- ET Prime: Premium business analysis, 70+ exclusive long-reads/month, ₹213/month
- ET Markets: Live BSE/NSE prices, Sensex/Nifty, portfolio tracking — Free
- ET Wealth: Personal finance, tax planning, SIPs, insurance — Free
- ET Masterclass: Executive seminars by PwC, KPMG, IIM faculty — ₹15K-50K
- ET Edge Summits: B2B industry conferences for CXOs — ₹5K-25K
- ET Entrepreneur Summit: Startup ecosystem events — ₹3K-10K
- ET Money: Commission-free mutual funds, SIP investing — Free
- ET Now: Live business TV streaming — Free
- ET Portfolio: Portfolio tracking, demat linking — Free

RULES:
- Ask ONE question at a time. Never two.
- Be warm and conversational, not form-like.
- Keep responses under 80 words.
- NEVER recommend products outside the ET ecosystem.
- After 4-5 turns, you have enough to make recommendations."""

PARAMETER temperature 0.3
PARAMETER num_predict 512
PARAMETER num_ctx 2048
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|end_of_text|>"
```

**Manglam runs:**
```bash
# Place the .gguf file in backend/ folder
cd backend
ollama create et-artha -f Modelfile
ollama run et-artha "Hello, I am a software engineer"
```

---

### TASK 4 — Recommendation Engine (Day 2 Morning)

Create `backend/recommender.py`:

```python
# backend/recommender.py
"""
Recommendation engine that maps UserProfile → ET product recommendations.
Works as a rule-based fallback when the LLM output is incomplete.
Uses Anuj's ChromaDB retriever for semantic matching.
"""

from knowledge.retriever import retrieve_for_profile

# Priority rules per archetype (guaranteed recommendations)
ARCHETYPE_PRIORITY_MAP = {
    "THE MARKET MAVERICK": [
        {
            "product": "ET Markets",
            "reason": "Live Nifty/Sensex prices, F&O data, and stock screener — built for active traders",
            "cta": "Track markets free",
            "url": "https://economictimes.indiatimes.com/markets",
            "priority": 1,
            "category": "finance"
        },
        {
            "product": "ET Prime",
            "reason": "In-depth market analysis and expert trading views published every morning",
            "cta": "Start 30-day free trial",
            "url": "https://economictimes.indiatimes.com/prime",
            "priority": 2,
            "category": "content"
        },
        {
            "product": "ET Now",
            "reason": "Live market commentary during trading hours from ET's market experts",
            "cta": "Watch live for free",
            "url": "https://etnow.com",
            "priority": 3,
            "category": "content"
        },
    ],
    "THE WEALTH BUILDER": [
        {
            "product": "ET Wealth",
            "reason": "Best beginner-to-intermediate guides on SIPs, goal-based investing, and tax planning",
            "cta": "Plan your finances free",
            "url": "https://economictimes.indiatimes.com/wealth",
            "priority": 1,
            "category": "finance"
        },
        {
            "product": "ET Money",
            "reason": "Direct mutual fund plans with 0% commission — you keep every rupee of returns",
            "cta": "Start SIP with ₹500",
            "url": "https://www.etmoney.com",
            "priority": 2,
            "category": "services"
        },
        {
            "product": "ET Prime",
            "reason": "Weekend reads on personal finance, market trends, and investment strategy",
            "cta": "Start 30-day free trial",
            "url": "https://economictimes.indiatimes.com/prime",
            "priority": 3,
            "category": "content"
        },
    ],
    "THE CORNER OFFICE": [
        {
            "product": "ET Prime",
            "reason": "Deep policy analysis, M&A coverage, and global macro insights for senior leaders",
            "cta": "Start 30-day free trial",
            "url": "https://economictimes.indiatimes.com/prime",
            "priority": 1,
            "category": "content"
        },
        {
            "product": "ET Masterclass",
            "reason": "Executive workshops by PwC, KPMG, and IIM faculty on finance and leadership",
            "cta": "View upcoming masterclasses",
            "url": "https://etmasterclass.economictimes.com",
            "priority": 2,
            "category": "education"
        },
        {
            "product": "ET Edge Summits",
            "reason": "Industry-specific conferences where sector CXOs network and set the agenda",
            "cta": "See upcoming summits",
            "url": "https://etedge.economictimes.com",
            "priority": 3,
            "category": "events"
        },
    ],
    "THE STARTUP SHERPA": [
        {
            "product": "ET Entrepreneur Summit",
            "reason": "Best event to meet Series A/B investors and fellow founders building at your stage",
            "cta": "Register for next summit",
            "url": "https://economictimes.indiatimes.com/small-biz",
            "priority": 1,
            "category": "events"
        },
        {
            "product": "ET Prime",
            "reason": "Startup funding news, policy for startups, and VC perspectives — all in one place",
            "cta": "Start 30-day free trial",
            "url": "https://economictimes.indiatimes.com/prime",
            "priority": 2,
            "category": "content"
        },
        {
            "product": "ET Masterclass",
            "reason": "Finance and strategy workshops relevant for founders building scalable businesses",
            "cta": "View upcoming masterclasses",
            "url": "https://etmasterclass.economictimes.com",
            "priority": 3,
            "category": "education"
        },
    ],
    "THE CAREFUL PLANNER": [
        {
            "product": "ET Wealth",
            "reason": "In-depth guides on FD rates, senior citizen savings, and insurance planning",
            "cta": "Plan your finances free",
            "url": "https://economictimes.indiatimes.com/wealth",
            "priority": 1,
            "category": "finance"
        },
        {
            "product": "ET Money",
            "reason": "Conservative MF options and insurance comparisons for risk-aware investors",
            "cta": "Compare plans free",
            "url": "https://www.etmoney.com",
            "priority": 2,
            "category": "services"
        },
    ],
    "THE CURIOUS LEARNER": [
        {
            "product": "ET Wealth",
            "reason": "Easy-to-understand financial literacy guides — perfect for building foundational knowledge",
            "cta": "Start learning free",
            "url": "https://economictimes.indiatimes.com/wealth",
            "priority": 1,
            "category": "finance"
        },
        {
            "product": "ET Money",
            "reason": "Start your first SIP with as little as ₹500 — guided, simple, and commission-free",
            "cta": "Start with ₹500",
            "url": "https://www.etmoney.com",
            "priority": 2,
            "category": "services"
        },
        {
            "product": "ET Markets",
            "reason": "Free portfolio tracker and market education tools — learn by watching live markets",
            "cta": "Track markets free",
            "url": "https://economictimes.indiatimes.com/markets",
            "priority": 3,
            "category": "finance"
        },
    ],
}


def get_recommendations(profile: dict, max_recs: int = 4) -> list[dict]:
    """
    Main recommendation function.
    
    Strategy:
    1. Start with archetype-based priority rules (guaranteed quality)
    2. Supplement with RAG-retrieved items for personalization
    3. Deduplicate and return top max_recs
    
    Args:
        profile: UserProfile dict from Anuj's extractor
        max_recs: Max recommendations to return
    
    Returns:
        List of recommendation dicts
    """
    archetype = profile.get("archetype", "THE CURIOUS LEARNER")

    # 1. Start with archetype priority rules
    base_recs = ARCHETYPE_PRIORITY_MAP.get(archetype, ARCHETYPE_PRIORITY_MAP["THE CURIOUS LEARNER"]).copy()

    # 2. Get RAG-based additional recommendations
    try:
        rag_items = retrieve_for_profile(profile, n_results=4)
        seen_products = {r["product"] for r in base_recs}

        for item in rag_items:
            if item["name"] not in seen_products:
                base_recs.append({
                    "product": item["name"],
                    "reason": _personalize_reason(item, profile),
                    "cta": item["cta"],
                    "url": item["url"],
                    "priority": len(base_recs) + 1,
                    "category": item["category"],
                })
                seen_products.add(item["name"])
    except Exception as e:
        print(f"RAG retrieval failed, using archetype rules only: {e}")

    return base_recs[:max_recs]


def _personalize_reason(item: dict, profile: dict) -> str:
    """
    Generate a personalized reason string for an RAG-retrieved item.
    """
    profession = profile.get("profession", "")
    goal = profile.get("goal", "")
    interests = profile.get("interests", [])

    # Use the document description, shortened
    desc = item.get("document", "")[:120]
    if profession:
        return f"Given your background in {profession} — {desc}..."
    if goal:
        return f"Aligns with your goal to {goal} — {desc}..."
    return desc + "..."
```

---

### TASK 5 — Archetype Classifier (Day 2 Morning)

Create `backend/archetype.py`:

```python
# backend/archetype.py
"""
Rule-based archetype classifier as a fast deterministic fallback.
Used when LLM profile extraction returns low confidence.
"""

from dataclasses import dataclass

@dataclass
class ArchetypeScore:
    archetype: str
    score: float
    signals: list[str]  # what triggered this score


ARCHETYPE_SIGNALS = {
    "THE MARKET MAVERICK": {
        "keywords": ["trade", "trading", "nifty", "sensex", "stocks", "f&o", "options", "futures",
                     "intraday", "swing", "technical analysis", "demat", "broker", "equity"],
        "professions": ["trader", "broker", "fund manager", "analyst"],
        "weight": 1.0
    },
    "THE WEALTH BUILDER": {
        "keywords": ["sip", "mutual fund", "invest", "goal", "wealth", "portfolio", "elss",
                     "long term", "retirement", "savings", "returns", "compounding"],
        "professions": ["engineer", "doctor", "teacher", "professional", "employee", "salaried"],
        "weight": 1.0
    },
    "THE CORNER OFFICE": {
        "keywords": ["cfo", "ceo", "cto", "cxo", "director", "vp", "head of", "president",
                     "macro", "policy", "strategy", "m&a", "corporate", "global", "board"],
        "professions": ["cfo", "ceo", "vp", "director", "head", "senior", "president", "executive"],
        "weight": 1.0
    },
    "THE STARTUP SHERPA": {
        "keywords": ["startup", "founder", "co-founder", "venture", "vc", "angel", "seed",
                     "series a", "fundraising", "pitch", "product", "scale", "entrepreneur"],
        "professions": ["founder", "co-founder", "entrepreneur", "startup", "cto of startup"],
        "weight": 1.0
    },
    "THE CAREFUL PLANNER": {
        "keywords": ["fd", "fixed deposit", "safe", "conservative", "risk averse", "insurance",
                     "retire", "pension", "ppf", "guaranteed", "protect", "secure"],
        "professions": ["retired", "near retirement", "government"],
        "weight": 1.0
    },
    "THE CURIOUS LEARNER": {
        "keywords": ["student", "just started", "beginner", "new to", "learning", "first time",
                     "understand", "how does", "explain", "basics", "college"],
        "professions": ["student", "fresher", "intern", "recent graduate"],
        "weight": 1.0
    },
}


def classify_archetype(conversation_text: str, profession: str = "") -> ArchetypeScore:
    """
    Classify user into one of 6 ET financial archetypes.
    Returns the best matching archetype with its score and signals.
    """
    text = (conversation_text + " " + profession).lower()

    scores = {}
    signals = {}

    for archetype, config in ARCHETYPE_SIGNALS.items():
        score = 0.0
        matched_signals = []

        # Check keywords in conversation
        for kw in config["keywords"]:
            if kw in text:
                score += 1.0 * config["weight"]
                matched_signals.append(f"keyword: '{kw}'")

        # Check profession keywords (higher weight)
        for prof in config["professions"]:
            if prof in profession.lower():
                score += 2.0 * config["weight"]
                matched_signals.append(f"profession: '{prof}'")

        scores[archetype] = score
        signals[archetype] = matched_signals

    if not any(scores.values()):
        # Default to Curious Learner if nothing matched
        return ArchetypeScore("THE CURIOUS LEARNER", 0.0, ["default"])

    best_archetype = max(scores, key=scores.get)
    return ArchetypeScore(
        archetype=best_archetype,
        score=scores[best_archetype],
        signals=signals[best_archetype]
    )


def validate_and_fix_profile(profile: dict, conversation: str = "") -> dict:
    """
    Validate LLM-extracted profile. If confidence is low, use rule-based classifier.
    """
    if not profile:
        return _default_profile()

    confidence = profile.get("profile_confidence", 0.5)

    # If low confidence, re-classify using rules
    if confidence < 0.6:
        profession = profile.get("profession", "")
        classifier_result = classify_archetype(conversation, profession)
        profile["archetype"] = classifier_result.archetype
        profile["classification_method"] = "rule_based"
    else:
        profile["classification_method"] = "llm_extracted"

    # Ensure required fields exist
    profile.setdefault("profession", "professional")
    profile.setdefault("experience", "intermediate")
    profile.setdefault("goal", "stay informed and grow wealth")
    profile.setdefault("interests", [])

    return profile


def _default_profile() -> dict:
    return {
        "archetype": "THE CURIOUS LEARNER",
        "profession": "professional",
        "experience": "beginner",
        "goal": "learn about personal finance",
        "interests": [],
        "profile_confidence": 0.3,
        "classification_method": "default"
    }
```

---

### TASK 6 — Test Your Fine-Tuned Model (Day 2, after fine-tuning)

Once Manglam has the model running in Ollama, test it:

```python
# test_model.py — run from backend/ folder
import asyncio
import httpx

OLLAMA_URL = "http://localhost:11434"
MODEL = "et-artha"

TEST_PROMPTS = [
    {
        "name": "Test 1: First message from user",
        "system": "You are ET Artha, the AI concierge for Economic Times.",
        "input": "Hi! I'm a software engineer, 28 years old, just started my first SIP.",
        "expected": "Should ask ONE follow-up question about goals or experience"
    },
    {
        "name": "Test 2: Profile extraction",
        "system": "Extract a UserProfile JSON. Respond ONLY with valid JSON.",
        "input": "USER: I'm a day trader. Trade Nifty options, 3 years experience.\nET ARTHA: What's your main challenge?\nUSER: Finding good entry points.",
        "expected": "Should return valid JSON with archetype: THE MARKET MAVERICK"
    },
    {
        "name": "Test 3: Stay in character",
        "system": "You are ET Artha, the AI concierge for Economic Times.",
        "input": "Can you help me book a flight to Mumbai?",
        "expected": "Should redirect to ET products, not help with flights"
    },
    {
        "name": "Test 4: Cross-sell trigger",
        "system": "You are ET Artha, the AI concierge for Economic Times.",
        "input": "I'm building a fintech startup and just closed our seed round.",
        "expected": "Should mention ET Entrepreneur Summit"
    },
]

async def test():
    async with httpx.AsyncClient(timeout=60.0) as client:
        for test in TEST_PROMPTS:
            print(f"\n{'='*50}")
            print(f"🧪 {test['name']}")
            print(f"Expected: {test['expected']}")
            print(f"Input: {test['input']}")

            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": MODEL,
                    "system": test["system"],
                    "prompt": test["input"],
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )
            response = r.json()["response"]
            print(f"Output: {response}")

asyncio.run(test())
```

**Run it:**
```bash
cd backend
python test_model.py
```

**Pass criteria:**
- Test 1: Asks exactly 1 question, under 80 words ✅
- Test 2: Returns valid parseable JSON with correct archetype ✅
- Test 3: Redirects to ET, doesn't help with flights ✅
- Test 4: Mentions ET Entrepreneur Summit ✅

If any test fails, adjust the Modelfile's SYSTEM prompt and re-run `ollama create et-artha -f Modelfile`.

---

### TASK 7 — Upload Model to HuggingFace Hub (Day 2, for team backup)

```bash
pip install huggingface_hub

python -c "
from huggingface_hub import HfApi, login
login()  # enter your HF token
api = HfApi()
api.create_repo('your-username/et-artha-llama3b', exist_ok=True)
api.upload_file(
    path_or_fileobj='et_artha_gguf/et-artha-llama3.2-3b-q4_k_m.gguf',
    path_in_repo='et-artha-q4_k_m.gguf',
    repo_id='your-username/et-artha-llama3b'
)
print('Done! Share the model URL with team.')
"
```

**Then Manglam can download it with:**
```bash
ollama pull hf.co/your-username/et-artha-llama3b
```

---

## ✅ Daily Checklist

### Day 1
- [ ] Google Colab notebook set up with T4 GPU
- [ ] Unsloth and dependencies installed in Colab
- [ ] Base Llama 3.2 3B loaded successfully
- [ ] LoRA adapters attached
- [ ] Training data received from Anuj (or seed data prepared)
- [ ] Training started (20-40 min, monitor loss)
- [ ] GGUF exported and downloaded
- [ ] Modelfile written and given to Manglam
- [ ] Model uploaded to HuggingFace Hub

### Day 2
- [ ] `recommender.py` written and tested
- [ ] `archetype.py` written and tested
- [ ] Model tested with 4 test prompts — all pass
- [ ] Manglam confirms `ollama run et-artha` works on his machine
- [ ] Anuj confirms agent is calling the model correctly

### Day 3
- [ ] Full end-to-end test: chat → profiling → archetype → recommendations
- [ ] Edge cases tested: vague user, off-topic user, very experienced user

---

## 🔌 Integration Contracts

### What you give Manglam:
- `Modelfile` — he runs `ollama create et-artha -f Modelfile`
- HuggingFace URL for the GGUF model (backup download)
- The exact model name to put in his `.env`: `OLLAMA_MODEL=et-artha`

### What you give Anuj:
- The exact model name string to use in his `concierge.py`: `"et-artha"`
- Confirm the JSON output format of profile extraction is stable

### What Anuj gives you:
- `data/training_data.json` — ASAP on Day 1

### What you expose to Manglam (importable functions):
```python
# He can import these if needed:
from recommender import get_recommendations
from archetype import validate_and_fix_profile, classify_archetype
```

---

## 🧠 Model Quality Tips

**If the model keeps asking too many questions:**
Add to Modelfile SYSTEM: `"You must complete profiling in exactly 4-5 turns. After turn 4, make recommendations regardless."`

**If JSON extraction is messy:**
The `concierge.py` already handles JSON parsing with fallbacks. Don't worry about perfect JSON every time.

**If the model goes off-topic:**
Add to Modelfile: `"If asked anything unrelated to ET products or personal finance, politely redirect: 'I'm here specifically to help you get the most from the ET ecosystem. Let me know what financial goals I can help with.'"`

**If responses are too long:**
In Modelfile: `PARAMETER num_predict 256` (reduces max output length)

---

*You are building the brain of ET Artha. The quality of the fine-tuned model determines how impressive the entire demo feels. Take your time on the training data quality — 50 excellent examples beat 300 mediocre ones.*

---

## ⚠️ Dependency & Conflict Map — What Blocks You and What Doesn't

### Your 1 real blocker

#### Blocker — Anuj's training data (Day 1 noon)
You cannot start fine-tuning until you have `training_data.json` from Anuj. He is sending you at least 30 seed examples by **12:00 PM Day 1**. Do not wait for all 300 — start fine-tuning immediately on 30 examples. You can do a second, better run with the full set later.

**What to do while waiting (9 AM – 12 PM):**

```
9:00 AM  — Open Google Colab, select T4 GPU runtime
9:15 AM  — Run Cell 1: install Unsloth (takes ~15 min — start this first!)
9:30 AM  — Run Cell 2: load Llama 3.2 3B base model (downloads ~2GB)
10:30 AM — Run Cell 3: attach LoRA adapters (instant)
10:35 AM — Write recommender.py (completely independent, no data needed)
11:30 AM — Write archetype.py (completely independent)
12:00 PM — Anuj sends training_data.json → upload in Colab Cell 4 → start training
```

The install + model download takes 30–45 minutes total, so if you start Colab at 9 AM, everything is ready to train the moment Anuj's data arrives.

---

### Things that do NOT block you (start these immediately)

| Task | Why you don't need to wait |
|---|---|
| Google Colab setup + Unsloth install | Independent — start first |
| Llama 3.2 3B base model download | Independent — runs in background |
| `recommender.py` | Pure Python logic, no model or data needed |
| `archetype.py` | Pure Python logic, no model or data needed |
| Writing the `Modelfile` | Just a text file, no model needed to write it |
| HuggingFace account setup | Independent |

---

### What you hand off to teammates and when

| Deliverable | Goes to | When |
|---|---|---|
| `data/training_data.json` acknowledgement | Anuj (confirm you received it) | Day 1 noon |
| `Modelfile` text file | Manglam | Day 1 evening (write it now, model name = `et-artha`) |
| `.gguf` file (or HuggingFace URL) | Manglam | Day 1 night / Day 2 morning after training finishes |
| Exact model name string: `"et-artha"` | Anuj (for `concierge.py`) | Day 2 morning |
| `recommender.py` + `archetype.py` | Manglam (place in `backend/`) | Day 2 morning |

---

### Critical: what Manglam does while waiting for your model

Manglam is NOT blocked by you. He runs:
```bash
ollama pull llama3.2:3b
```
And sets `OLLAMA_MODEL=llama3.2:3b` in his `.env`. The entire system works with this placeholder. When your GGUF is ready, he swaps one line. You do not need to rush and produce a bad model — take the time to train it properly.

---

### Day 1 order of operations for you

```
9:00 AM  — Open Colab, select T4 GPU, run Cell 1 (Unsloth install — 15 min)
9:20 AM  — Run Cell 2 (model download — 20 min, runs in background)
9:20 AM  — While downloading: write recommender.py
10:30 AM — While model finishes: write archetype.py
11:00 AM — Write Modelfile, send to Manglam on WhatsApp
11:30 AM — Run Cell 3 (LoRA adapters — instant)
12:00 PM — Receive training_data.json from Anuj → upload → run Cell 4+5
12:30 PM — Training starts (watch loss go down, target < 0.8)
1:00 PM  — Training done → run Cell 6 (GGUF export — 5–10 min)
1:30 PM  — Send GGUF to Manglam (Google Drive link or HuggingFace URL)
2:00 PM  — Run Cell 7 (upload to HuggingFace as backup)
3:00 PM  — Run test_model.py with Manglam to verify model works
```
