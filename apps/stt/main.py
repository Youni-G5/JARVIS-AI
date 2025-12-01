from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from datetime import datetime
from whisper_engine import WhisperEngine

app = FastAPI(title="JARVIS STT Service", version="0.2.0")

# Initialiser Whisper
model_size = os.getenv("WHISPER_MODEL_SIZE", "base")  # tiny, base, small, medium, large
device = os.getenv("WHISPER_DEVICE", "cpu")  # cpu ou cuda
compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")  # int8, float16, float32

whisper_engine = WhisperEngine(
    model_size=model_size,
    device=device,
    compute_type=compute_type
)

class TranscriptResponse(BaseModel):
    text: str
    confidence: float
    language: str
    duration: float
    timestamp: str
    segments: list = []
    processing_time: Optional[float] = None

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "stt",
        "model": model_size,
        "whisper_loaded": whisper_engine.model is not None,
        "device": device
    }

@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcrit un fichier audio en texte.
    Formats supportés: WAV, MP3, OGG, FLAC, M4A
    """
    try:
        # Valider le format
        allowed_formats = [".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm"]
        file_ext = os.path.splitext(audio.filename)[1].lower()
        
        if file_ext not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté. Formats autorisés: {', '.join(allowed_formats)}"
            )
        
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Transcrire
        result = whisper_engine.transcribe(tmp_path, language=language)
        
        # Nettoyer
        os.unlink(tmp_path)
        
        # Vérifier si erreur
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return TranscriptResponse(
            text=result["text"],
            confidence=result["confidence"],
            language=result["language"],
            duration=result["duration"],
            timestamp=datetime.utcnow().isoformat(),
            segments=result.get("segments", []),
            processing_time=result.get("processing_time")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/stream")
async def transcribe_stream(audio_chunk: UploadFile = File(...)):
    """
    Transcription streaming (temps réel).
    TODO: Améliorer avec buffer et gestion de chunks continus
    """
    try:
        contents = await audio_chunk.read()
        result = whisper_engine.transcribe_realtime(contents)
        
        return {
            "partial_text": result["text"],
            "confidence": result["confidence"],
            "is_final": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/languages")
async def list_languages():
    """Liste des langues supportées par Whisper."""
    return {
        "languages": [
            {"code": "fr", "name": "Français"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "de", "name": "Deutsch"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Português"},
            {"code": "nl", "name": "Nederlands"},
            {"code": "pl", "name": "Polski"},
            {"code": "ru", "name": "Русский"},
            {"code": "ja", "name": "日本語"},
            {"code": "zh", "name": "中文"},
            {"code": "ar", "name": "العربية"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)