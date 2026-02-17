import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("../data/podcasts.json", "r") as f:
    podcasts = json.load(f)

embeddings = []

for p in podcasts:
    vec = model.encode(p["description"])
    embeddings.append(vec.tolist())

output = {
    "podcasts": podcasts,
    "embeddings": embeddings
}

with open("../data/embeddings.json", "w") as f:
    json.dump(output, f)

print("Embeddings saved to data/embeddings.json")
