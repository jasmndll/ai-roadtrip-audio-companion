import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("../data/embeddings.json", "r") as f:
    data = json.load(f)

podcasts = data["podcasts"]
embeddings = np.array(data["embeddings"])

def recommend(duration, mood):
    query_vec = model.encode(mood)

    similarities = embeddings @ query_vec / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
    )

    candidates = [
        (i, sim)
        for i, sim in enumerate(similarities)
        if podcasts[i]["duration"] <= duration
    ]

    ranked = sorted(candidates, key=lambda x: x[1], reverse=True)

    playlist = []
    remaining = duration

    for i, _ in ranked:
        ep = podcasts[i]
        if ep["duration"] <= remaining:
            playlist.append(ep)
            remaining -= ep["duration"]

        if remaining <= 5:  # stop when trip nearly full
            break

    return {
        "playlist": playlist,
        "unused_minutes": remaining
    }

if __name__ == "__main__":
    print(recommend(60, "funny"))
