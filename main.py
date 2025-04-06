import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
from fastapi.responses import StreamingResponse
from bson import ObjectId
import io

# Configuration
MONGO_URI = "mongodb+srv://admin:Frozen12@dbclusterassignment.dkqp6jq.mongodb.net/testDB?retryWrites=true&w=majority&appName=DBClusterAssignment"
DB_NAME = "DBClusterAssignment"
SPRITES_COLLECTION = "Sprites"
AUDIO_COLLECTION = "Audio"
SCORES_COLLECTION = "Scores"

# FastAPI instance
app = FastAPI()

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Pydantic model for player scores
class PlayerScore(BaseModel):
    player_name: str
    score: int

# Upload Sprite
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db[SPRITES_COLLECTION].insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Get Sprite
@app.get("/sprite/{sprite_id}")
async def get_sprite(sprite_id: str):
    sprite = await db[SPRITES_COLLECTION].find_one({"_id": ObjectId(sprite_id)})
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return StreamingResponse(io.BytesIO(sprite["content"]), media_type="image/png")

# Upload Audio
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db[AUDIO_COLLECTION].insert_one(audio_doc)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

# Get Audio
@app.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    audio = await db[AUDIO_COLLECTION].find_one({"_id": ObjectId(audio_id)})
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return StreamingResponse(io.BytesIO(audio["content"]), media_type="audio/mpeg")

# Upload Score
@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db[SCORES_COLLECTION].insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# Get Scores
@app.get("/player_scores")
async def get_scores():
    scores = []
    cursor = db[SCORES_COLLECTION].find()
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        scores.append(doc)
    return scores
