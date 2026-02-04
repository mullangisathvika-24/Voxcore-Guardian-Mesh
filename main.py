
from fastapi import FastAPI, Depends, HTTPException, Security, UploadFile, File
from fastapi.security.api_key import APIKeyHeader

# 1. Configuration
API_KEY = "VOXCORE_2026_SECURE" # You can change this to any secret word
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="VoxCore Guardian Mesh")

# 2. Security Logic
async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return header_key
    raise HTTPException(status_code=403, detail="Access Denied: Invalid API Key")

# 3. HOME ROUTE (To fix the 404 error)
@app.get("/")
def home():
    return {"message": "VoxCore API is Online. Visit /docs to test."}

# 4. PROTECTED DETECTION ROUTE
@app.post("/detect")
async def detect_voice(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    # Your librosa/AI logic remains here
    return {"status": "Success", "classification": "Human"}
import base64
import os
import uuid
import librosa
import numpy as np
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated
app = FastAPI(title="Guardian Mesh: AI Voice Detection API")

# --- SECURITY ---
# Change this to your secret key. Set it in your Render/Railway Env Variables.
SECRET_API_KEY = os.getenv("API_KEY", "Sathvika_Guardian_2026")

# --- DATA STRUCTURE ---
class VoiceRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

# --- THE LOGIC: Prosodic Pulse Tracking (PPT) ---
def analyze_audio_ppt(file_path: str):
    """
    Simulates Prosodic Pulse Tracking by measuring rhythmic variance.
    AI voices often have 'too perfect' timing or mechanical micro-resets.
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        
        # 1. Extract Rhythmic Features (Onsets)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        pulse_variance = np.var(onset_env)

        # 2. Decision Logic
        # Humans have higher rhythmic variance; AI is often flatter/monotone.
        if pulse_variance > 1.2:  # Threshold for demonstration
            classification = "HUMAN"
            score = round(float(min(0.98, pulse_variance / 2.0)), 2)
            explanation = "Natural prosodic variance and organic speech pulses detected."
        else:
            classification = "AI_GENERATED"
            score = 0.96
            explanation = "Prosodic Pulse Tracking detected synthetic timing resets and mechanical rhythm."

        return classification, score, explanation

    except Exception as e:
        return "ERROR", 0.0, f"Analysis Error: {str(e)}"

# --- REST API ENDPOINT ---
@app.post("/api/voice-detection")
async def detect_voice(
    request: VoiceRequest, 
    x_api_key: Annotated[str | None, Header()] = None
):
    # 1. Validate API Key
    if x_api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Generate Unique Filename (Concurrency Protection)
    temp_filename = f"audio_{uuid.uuid4()}.mp3"

    try:
        # 3. Decode Base64 Audio
        audio_content = base64.b64decode(request.audioBase64)
        with open(temp_filename, "wb") as f:
            f.write(audio_content)

        # 4. Run PPT Analysis
        classification, score, explanation = analyze_audio_ppt(temp_filename)

        if classification == "ERROR":
            return {"status": "error", "message": explanation}

        # 5. Return JSON (Matches Hackathon Requirements)
        return {
            "status": "success",
            "language": request.language,
            "classification": classification,
            "confidenceScore": score,
            "explanation": f"{explanation} [Guardian Mesh Protocol]"
        }

    finally:
        # 6. Cleanup to keep the server clean
        if os.path.exists(temp_filename):
            os.remove(temp_filename)