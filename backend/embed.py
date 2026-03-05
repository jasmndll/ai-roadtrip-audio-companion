import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Paths ─────────────────────────────────────────────────────────────────────
# Always resolve paths relative to this script's location.
# This way it works no matter which folder you run it from.
BASE      = Path(__file__).parent.parent
IN_PATH   = BASE / "data" / "podcasts.json"
OUT_PATH  = BASE / "data" / "embeddings.json"

# ── Load podcasts ─────────────────────────────────────────────────────────────
# encoding="utf-8" is critical on Windows.
# Without it, Python uses cp1252 (Windows default) which crashes on
# international characters like accented letters, emoji, etc.
with open(IN_PATH, "r", encoding="utf-8") as f:
    podcasts = json.load(f)

print(f"Loaded {len(podcasts)} podcasts. Generating embeddings...")

# ── Generate embeddings ───────────────────────────────────────────────────────
# model.encode() converts each description string into a vector of 384 numbers.
# These numbers capture the *meaning* of the text, not just the words.
# Two descriptions about similar topics will have similar vectors.
embeddings = []

for i, p in enumerate(podcasts):
    vec = model.encode(p["description"])
    embeddings.append(vec.tolist())

    # Show progress every 20 podcasts
    if (i + 1) % 20 == 0 or (i + 1) == len(podcasts):
        print(f"  {i + 1}/{len(podcasts)} embedded...")

# ── Save output ───────────────────────────────────────────────────────────────
output = {
    "podcasts":   podcasts,
    "embeddings": embeddings
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False)

print(f"\n✅ Embeddings saved to {OUT_PATH}")
print("You can now start the server: python -m uvicorn main:app --reload")
