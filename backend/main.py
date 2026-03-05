from fastapi import FastAPI
from pydantic import BaseModel
from recommender import recommend
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ── Load .env file ────────────────────────────────────────────────────────────
# This runs when uvicorn starts the server.
# Any variables in backend/.env become available via os.getenv() everywhere.
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request model ─────────────────────────────────────────────────────────────
# Pydantic automatically validates incoming JSON.
# If the request is missing 'duration' or 'mood', FastAPI returns a 422 error
# with a helpful message instead of crashing.
class TripRequest(BaseModel):
    duration: int
    mood: str

@app.get("/")
def home():
    return {"message": "Roadtrip AI backend is running ✅"}

@app.post("/recommend")
def recommend_trip(trip: TripRequest):
    result = recommend(trip.duration, trip.mood)
    return result
