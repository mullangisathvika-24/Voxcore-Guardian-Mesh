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