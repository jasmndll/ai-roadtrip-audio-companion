from fastapi import FastAPI
from pydantic import BaseModel
from recommender import recommend
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    duration: int
    mood: str

@app.get("/")
def home():
    return {"message": "Roadtrip AI backend running"}

@app.post("/recommend")
def recommend_trip(trip: TripRequest):
    result = recommend(trip.duration, trip.mood)
    return result
