import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Path fix ──────────────────────────────────────────────────────────────────
# __file__ is the path to THIS script (recommender.py).
# .parent gives the folder it lives in (backend/).
# Going up one level (.parent.parent) reaches the project root.
# Then we go into data/embeddings.json from there.
# This means the path works correctly no matter where you run uvicorn from.
DATA_PATH = Path(__file__).parent.parent / "data" / "embeddings.json"

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"\n\nCould not find: {DATA_PATH}\n"
        "Run update_data.py first to generate embeddings:\n"
        "  python update_data.py\n"
    )

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

podcasts   = data["podcasts"]
embeddings = np.array(data["embeddings"])


def recommend(duration: int, mood: str) -> dict:
    """
    Given a trip duration (minutes) and a mood string,
    return a playlist of podcasts that fit the time and match the vibe.

    HOW IT WORKS:
    1. We encode the mood string into a vector (list of numbers).
    2. We compare it to every podcast's vector using cosine similarity.
       Cosine similarity measures the angle between two vectors — the smaller
       the angle, the more similar the meaning. Score ranges from -1 to 1.
    3. We filter to podcasts that fit in the remaining time.
    4. We greedily fill the trip, picking the best-matching podcast each time.
    """

    # Step 1: encode the mood into the same vector space as podcast descriptions
    query_vec = model.encode(mood)

    # Step 2: cosine similarity = (A · B) / (|A| * |B|)
    # embeddings @ query_vec  →  dot product of each podcast vector with the query
    # np.linalg.norm(...)     →  the magnitude (length) of each vector
    similarities = embeddings @ query_vec / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
    )

    # Step 3: sort all podcasts by similarity score (highest first)
    ranked_indices = np.argsort(similarities)[::-1]

    # Step 4: greedily fill the playlist within the time budget
    playlist  = []
    remaining = duration

    for i in ranked_indices:
        ep = podcasts[i]
        if ep["duration"] <= remaining:
            playlist.append(ep)
            remaining -= ep["duration"]

        if remaining <= 5:  # close enough — stop filling
            break

    return {
        "playlist": playlist,
        "unused_minutes": remaining
    }


# ── Quick test when you run this file directly ──
if __name__ == "__main__":
    result = recommend(90, "funny and light-hearted")
    print(f"\nFound {len(result['playlist'])} episodes:")
    for ep in result["playlist"]:
        print(f"  • {ep['title']} ({ep['duration']} min)")
    print(f"Unused: {result['unused_minutes']} min")
