import os
import requests
import hashlib
import time
import json

# --- Load API credentials from environment ---
API_KEY = os.getenv("PODCAST_KEY")
API_SECRET = os.getenv("PODCAST_SECRET")

if not API_KEY or not API_SECRET:
    print("ERROR: Missing API credentials.")
    print("Set environment variables first:")
    print("$env:PODCAST_KEY='your_key'")
    print("$env:PODCAST_SECRET='your_secret'")
    exit()

# --- Build authenticated request ---
url = "https://api.podcastindex.org/api/1.0/search/byterm?q=travel"

timestamp = str(int(time.time()))
auth_string = API_KEY + API_SECRET + timestamp
auth_hash = hashlib.sha1(auth_string.encode("utf-8")).hexdigest()

headers = {
    "X-Auth-Key": API_KEY,
    "X-Auth-Date": timestamp,
    "Authorization": auth_hash,
    "User-Agent": "roadtrip-ai"
}

# --- Send request ---
response = requests.get(url, headers=headers)

print("STATUS:", response.status_code)
print("RAW RESPONSE:", response.text[:500])  # print first 500 chars

if response.status_code != 200:
    print("API request failed.")
    exit()

data = response.json()

# --- Convert to dataset format ---
podcasts = []

for p in data.get("feeds", [])[:20]:
    podcasts.append({
        "title": p.get("title", ""),
        "description": p.get("description", ""),
        "duration": 45,   # placeholder until we parse real durations
        "genre": "mixed"
    })

# --- Save dataset ---
with open("../data/podcasts.json", "w", encoding="utf-8") as f:
    json.dump(podcasts, f, indent=2)

print("Live podcasts saved to data/podcasts.json")
