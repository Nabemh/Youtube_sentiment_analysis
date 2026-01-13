from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.inference.video_sentiment import analyse_video

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyse/{video_id}")
async def analyse(video_id: str):
    result = analyse_video(video_id)
    return result
