import os
import requests
import hashlib
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env file ────────────────────────────────────────────────────────────
# load_dotenv() looks for a file called .env in the current folder (backend/).
# It reads each line and sets them as environment variables automatically.
# This means you never need to run $env:PODCAST_KEY=... in PowerShell again.
load_dotenv()

# ── API credentials ───────────────────────────────────────────────────────────
API_KEY    = os.getenv("PODCAST_KEY")
API_SECRET = os.getenv("PODCAST_SECRET")

if not API_KEY or not API_SECRET:
    print("ERROR: Missing API credentials.")
    print("Create a file called .env inside your backend/ folder with:")
    print("  PODCAST_KEY=your_key")
    print("  PODCAST_SECRET=your_secret")
    exit()

# ── Where to save the output ──────────────────────────────────────────────────
# Path(__file__) = this script's location (backend/fetch_podcasts.py)
# Going up two levels lands us at the project root, then into data/
OUT_PATH = Path(__file__).parent.parent / "data" / "podcasts.json"

# ── Search terms — each maps to a mood the user might enter ──────────────────
# We search multiple terms so the recommender has diverse podcasts to choose from.
# More variety = better mood matching for non-travel vibes like "funny" or "science".
SEARCH_TERMS = [
    ("travel",     "travel"),
    ("comedy",     "comedy"),
    ("science",    "science"),
    ("history",    "history"),
    ("true crime", "true crime"),
    ("mindfulness","chill"),
    ("technology", "tech"),
    ("storytelling","storytelling"),
]

# ── Helper: build authenticated headers for PodcastIndex API ─────────────────
# The API uses a hash-based auth scheme:
# hash = SHA1(api_key + api_secret + unix_timestamp)
# This proves we have the secret without sending it in plain text.
def make_headers() -> dict:
    timestamp   = str(int(time.time()))
    auth_string = API_KEY + API_SECRET + timestamp
    auth_hash   = hashlib.sha1(auth_string.encode("utf-8")).hexdigest()
    return {
        "X-Auth-Key":   API_KEY,
        "X-Auth-Date":  timestamp,
        "Authorization": auth_hash,
        "User-Agent":   "roadtrip-ai"
    }

# ── Helper: get real episode duration ────────────────────────────────────────
# The PodcastIndex API returns `averageEpisodeDuration` in SECONDS.
# We convert to minutes and clamp to a sensible range (10–120 min).
# If the field is missing or zero, we fall back to 40 minutes.
def parse_duration(feed: dict) -> int:
    raw_seconds = feed.get("averageEpisodeDuration", 0)
    if raw_seconds and raw_seconds > 0:
        minutes = round(raw_seconds / 60)
        return max(10, min(minutes, 120))  # clamp: 10 min ≤ duration ≤ 120 min
    return 40  # fallback if API didn't provide it

# ── Fetch podcasts for one search term ───────────────────────────────────────
def fetch_for_term(term: str, genre_label: str, max_results: int = 15) -> list:
    url = f"https://api.podcastindex.org/api/1.0/search/byterm?q={requests.utils.quote(term)}&max={max_results}"
    
    try:
        response = requests.get(url, headers=make_headers(), timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Network error for '{term}': {e}")
        return []

    if response.status_code != 200:
        print(f"  ⚠️  API returned {response.status_code} for '{term}'")
        return []

    feeds = response.json().get("feeds", [])
    results = []

    for feed in feeds:
        title       = feed.get("title", "").strip()
        description = feed.get("description", "").strip()

        # Skip podcasts with no description — they're useless for embedding
        if not title or not description or len(description) < 30:
            continue

        results.append({
            "title":       title,
            "description": description,
            "duration":    parse_duration(feed),
            "genre":       genre_label,
            # Store the feed URL so you could link to it later
            "url":         feed.get("url", ""),
        })

    print(f"  ✓ '{term}' → {len(results)} podcasts fetched")
    return results

# ── Main: loop all search terms ───────────────────────────────────────────────
def main():
    all_podcasts = []
    seen_titles  = set()  # deduplicate — some podcasts appear in multiple searches

    print("\nFetching podcasts from PodcastIndex...\n")

    for term, genre in SEARCH_TERMS:
        results = fetch_for_term(term, genre)

        for pod in results:
            # Normalise title for dedup check (lowercase, strip spaces)
            key = pod["title"].lower().strip()
            if key not in seen_titles:
                seen_titles.add(key)
                all_podcasts.append(pod)

        # Be polite to the API — wait 0.5s between requests
        # (PodcastIndex is free but rate-limits aggressive scrapers)
        time.sleep(0.5)

    print(f"\n✅ Total unique podcasts collected: {len(all_podcasts)}")

    # Save to data/podcasts.json
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_podcasts, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved to {OUT_PATH}")
    print("\nNow run:  python embed.py   (or python update_data.py)")

if __name__ == "__main__":
    main()
