import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure .env is loaded
env_file = Path(__file__).resolve().parent / ".env"
if env_file.is_file():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

from sarvamai import SarvamAI
from pipeline import WellnessCoachExtractor, WellnessCheckInResult

app = FastAPI(title="Sarvam Indic Wellness Coach")

# Static files directory
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize Sarvam client & extractor
api_key = os.environ.get("SARVAM_API_KEY")
client = SarvamAI(api_subscription_key=api_key) if api_key else None
extractor = WellnessCoachExtractor(api_key=api_key) if api_key else None


class CheckInRequest(BaseModel):
    transcript: str
    generate_audio: bool = True
    speaker: str = "ishita"
    language_code: str = "hi-IN"


class CheckInResponse(BaseModel):
    data: WellnessCheckInResult
    audio_base64: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = static_dir / "index.html"
    if index_file.is_file():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Frontend index.html not found</h1>", status_code=404)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "api_key_configured": bool(os.environ.get("SARVAM_API_KEY"))}


@app.post("/api/checkin", response_model=CheckInResponse)
async def process_checkin(req: CheckInRequest):
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Check-in text cannot be empty.")

    global extractor, client
    if not extractor or not client:
        current_key = os.environ.get("SARVAM_API_KEY")
        if not current_key:
            raise HTTPException(status_code=500, detail="SARVAM_API_KEY is not configured.")
        client = SarvamAI(api_subscription_key=current_key)
        extractor = WellnessCoachExtractor(api_key=current_key)

    try:
        # Step 1: Extract structured health data
        result = extractor.extract(req.transcript)

        # Step 2: Generate spoken audio nudge with Bulbul v3 TTS
        audio_b64 = None
        if req.generate_audio and result.coach_feedback.spoken_nudge:
            try:
                tts_res = client.text_to_speech.convert(
                    text=result.coach_feedback.spoken_nudge,
                    language_code=req.language_code,
                    speaker=req.speaker,
                    model="bulbul:v3"
                )
                if tts_res.audios:
                    audio_b64 = tts_res.audios[0]
            except Exception as tts_err:
                print("TTS Warning (continuing without audio):", tts_err)

        return CheckInResponse(data=result, audio_base64=audio_b64)

    except Exception as e:
        print("Processing error:", e)
        raise HTTPException(status_code=500, detail=str(e))
