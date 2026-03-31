

# ══════════════════════════════════════════════
# CELL 1 — Install dependencies (run first! takes ~15 min)
# ══════════════════════════════════════════════
"""
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" -q
!pip install --no-deps trl peft accelerate bitsandbytes -q
!pip install datasets huggingface_hub -q
print("✅ All dependencies installed")
"""


# ══════════════════════════════════════════════
# CELL 2 — Load base model (Llama 3.2 3B Instruct, 4-bit)
# ══════════════════════════════════════════════
"""
from unsloth import FastLanguageModel
import torch

MAX_SEQ_LENGTH = 2048   # max context window
DTYPE = None            # auto-detect (float16 on T4)
LOAD_IN_4BIT = True     # 4-bit quantization fits in 15 GB T4 VRAM

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-3B-Instruct",
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = DTYPE,
    load_in_4bit = LOAD_IN_4BIT,
)

print("✅ Base model loaded:", model.config.name_or_path)
print(f"   Parameters : {model.num_parameters()/1e6:.1f}M")
print(f"   VRAM used  : {torch.cuda.memory_allocated()/1e9:.2f} GB")
"""


# ══════════════════════════════════════════════
# CELL 3 — Attach LoRA adapters (the actual fine-tuning magic)
# ══════════════════════════════════════════════
"""
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,                          # LoRA rank — 16 is the sweet spot for quality/speed
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",   # attention
        "gate_proj", "up_proj", "down_proj",        # MLP
    ],
    lora_alpha = 16,
    lora_dropout = 0,                # 0 is optimised by Unsloth
    bias = "none",
    use_gradient_checkpointing = "unsloth",   # saves ~30% VRAM
    random_state = 42,
    use_rslora = False,
)

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print("✅ LoRA adapters attached")
print(f"   Trainable params : {trainable/1e6:.2f}M  ({100*trainable/total:.1f}% of total)")
"""


# ══════════════════════════════════════════════
# CELL 4 — Load & format training data
# ══════════════════════════════════════════════
"""
import json
from datasets import Dataset
from collections import Counter

# ── Option A: Upload from your machine ──────────────
from google.colab import files
print("📁 Upload training_data.json:")
uploaded = files.upload()
filename = list(uploaded.keys())[0]

# ── Option B: If the file is already present in this session ────────
# filename = "training_data.json"  # uncomment this line instead

with open(filename) as f:
    raw_data = json.load(f)

print(f"✅ Loaded {len(raw_data)} training examples")

# Show breakdown of instruction types (useful to verify data quality)
instruction_types = Counter()
for ex in raw_data:
    inst = ex["instruction"].lower()
    if "extract" in inst or "json" in inst and "profile" in inst:
        instruction_types["profile_extraction"] += 1
    elif "recommend" in inst:
        instruction_types["recommendation"] += 1
    elif "cross-sell" in inst:
        instruction_types["cross_sell"] += 1
    elif "handle" in inst:
        instruction_types["edge_case"] += 1
    else:
        instruction_types["follow_up_question"] += 1

print("\n📊 Dataset breakdown:")
for k, v in instruction_types.most_common():
    print(f"   {k}: {v} examples")

# ── Format for Llama 3.2 Instruct chat template ─────
def format_example(example):
    instruction = example["instruction"]
    user_input  = example["input"]
    output      = example["output"]

    # Llama 3.2 Instruct special tokens
    text = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{instruction}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_input}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        f"{output}<|eot_id|>"
    )
    return {"text": text}

formatted = [format_example(ex) for ex in raw_data]
dataset   = Dataset.from_list(formatted)

print(f"\n✅ Dataset formatted: {len(dataset)} examples")
print("\nSample (first 400 chars):")
print(dataset[0]["text"][:400])
"""


# ══════════════════════════════════════════════
# CELL 5 — Train (20-40 min on T4 GPU)
# ══════════════════════════════════════════════
"""
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# ── Training params tuned for the actual 38-example dataset ──────────
# With only 38 examples, we train more epochs so the model sees enough variation.
# Effective batch = per_device(2) × grad_accum(4) = 8
# Steps per epoch = ceil(38 / 8) = 5 steps → 5 steps × 5 epochs = 25 total steps
NUM_EXAMPLES = len(dataset)  # should be 38 from training_data.json
EPOCHS       = 5 if NUM_EXAMPLES < 100 else 3   # more epochs for small dataset
WARMUP       = max(3, int(0.1 * (NUM_EXAMPLES // 8) * EPOCHS))  # 10% of total steps

print(f"📊 Training config: {NUM_EXAMPLES} examples, {EPOCHS} epochs, {WARMUP} warmup steps")

trainer = SFTTrainer(
    model              = model,
    tokenizer          = tokenizer,
    train_dataset      = dataset,
    dataset_text_field = "text",
    max_seq_length     = MAX_SEQ_LENGTH,
    dataset_num_proc   = 2,
    args = TrainingArguments(
        per_device_train_batch_size  = 2,
        gradient_accumulation_steps  = 4,       # effective batch = 8
        warmup_steps                 = WARMUP,
        num_train_epochs             = EPOCHS,
        learning_rate                = 2e-4,
        fp16                         = not is_bfloat16_supported(),
        bf16                         = is_bfloat16_supported(),
        logging_steps                = 1,
        optim                        = "adamw_8bit",
        weight_decay                 = 0.01,
        lr_scheduler_type            = "linear",
        output_dir                   = "et_artha_output",
        seed                         = 42,
        report_to                    = "none",  # disable wandb
    ),
)

print("🏋️  Starting fine-tuning...")
print("    Watch the loss — target: start ~2.0, end < 0.8")
print(f"   Estimated time on T4: {max(5, NUM_EXAMPLES // 5)}-{max(15, NUM_EXAMPLES // 2)} minutes\n")

trainer_stats = trainer.train()

print(f"\n✅ Training complete!")
print(f"   Peak VRAM : {torch.cuda.max_memory_reserved()/1e9:.2f} GB")
print(f"   Time      : {trainer_stats.metrics['train_runtime']/60:.1f} min")
print(f"   Final loss: {trainer_stats.metrics['train_loss']:.4f}")
if trainer_stats.metrics['train_loss'] > 1.0:
    print("⚠️  Loss is still high (>1.0). Consider increasing epochs or checking data quality.")
"""


# ══════════════════════════════════════════════
# CELL 6 — Export to GGUF (for Ollama)
# ══════════════════════════════════════════════
"""
import os

# Save LoRA adapter (small — good to keep)
model.save_pretrained("et_artha_lora")
tokenizer.save_pretrained("et_artha_lora")
print("✅ LoRA adapter saved to et_artha_lora/")

# Export GGUF — q4_k_m = good quality/size balance (~2 GB)
print("\\n📦 Exporting to GGUF (5-10 min)...")
model.save_pretrained_gguf(
    "et_artha_gguf",
    tokenizer,
    quantization_method = "q4_k_m",
)
print("✅ GGUF exported!")

gguf_files = [f for f in os.listdir("et_artha_gguf") if f.endswith(".gguf")]
for f in gguf_files:
    size = os.path.getsize(f"et_artha_gguf/{f}") / 1e9
    print(f"   {f}  →  {size:.2f} GB")
"""


# ══════════════════════════════════════════════
# CELL 7 — Upload GGUF to HuggingFace Hub (team backup)
# ══════════════════════════════════════════════
"""
import getpass
from huggingface_hub import login, HfApi

# 1. Create free account at huggingface.co
# 2. Get token: huggingface.co/settings/tokens  (write access)
hf_token = getpass.getpass("Enter your HuggingFace token: ")
login(token=hf_token)

YOUR_HF_USERNAME = "your-hf-username"   # ← CHANGE THIS
repo_id = f"{YOUR_HF_USERNAME}/et-artha-llama3.2-3b"

api = HfApi()
api.create_repo(repo_id=repo_id, exist_ok=True)
api.upload_folder(
    folder_path = "et_artha_gguf",
    repo_id     = repo_id,
    repo_type   = "model",
)

hf_url = f"https://huggingface.co/{repo_id}"
print(f"\\n✅ Model uploaded!")
print(f"   HuggingFace URL: {hf_url}")
print(f"\\n📤 Share with Manglam:")
print(f"   ollama pull hf.co/{repo_id}")
"""


# ══════════════════════════════════════════════
# CELL 8 — Download GGUF to your local machine
# ══════════════════════════════════════════════
"""
import os
from google.colab import files

gguf_files = [f for f in os.listdir("et_artha_gguf") if f.endswith(".gguf")]

for f in gguf_files:
    print(f"Downloading {f} ...")
    files.download(f"et_artha_gguf/{f}")

print("\\n✅ Download started!")
print("   Save this .gguf file → send to Manglam via Google Drive / WeTransfer / USB")
print("   Manglam places it in backend/ and runs: ollama create et-artha -f Modelfile")
"""


# ══════════════════════════════════════════════
# CELL 9 (optional) — Quick test inside Colab before downloading
# ══════════════════════════════════════════════
"""
# Quick in-Colab smoke tests — inputs taken directly from training_data.json

FastLanguageModel.for_inference(model)   # switch to fast inference mode

def chat(user_msg: str, system_msg: str = None) -> str:
    if system_msg is None:
        system_msg = (
            "You are ET Artha, the personal AI concierge for The Economic Times ecosystem. "
            "Understand who the user is in 4-5 questions, then recommend ET products. "
            "Keep responses under 80 words. Ask ONE question at the end."
        )

    messages = [
        {"role": "system",    "content": system_msg},
        {"role": "user",      "content": user_msg},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to("cuda")

    outputs = model.generate(
        input_ids      = inputs,
        max_new_tokens = 256,
        temperature    = 0.3,
        do_sample      = True,
    )
    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    return response.strip()

# Inputs taken directly from training_data.json
test_inputs = [
    # Follow-up questions
    ("Hi",                                           "Should ask who they are — handle vague intro"),
    ("I trade stocks daily. Nifty 50 and some F&O.", "Should ask intraday vs swing"),
    ("I'm a software engineer, 28. Just started SIP.","Should ask about goal/purpose"),
    # Cross-sell triggers
    ("I'm a founder. Just closed our seed round.",   "Should mention ET Entrepreneur Summit"),
    ("I've been doing SIP for 6 months.",            "Should mention direct plans / ET Money"),
    ("I'm trying to save tax before March 31.",      "Should mention ELSS / ET Wealth"),
    # Off-topic redirect
    ("Can you recommend a good Zerodha plan?",       "Should redirect to ET Markets, not Zerodha"),
]

print("\n" + "="*60)
print("  In-Colab Model Test (inputs from training_data.json)")
print("="*60)
for msg, expected in test_inputs:
    print(f"\nUser     : {msg}")
    print(f"Expected : {expected}")
    print(f"ET Artha : {chat(msg)}")
    print("-" * 50)
"""
