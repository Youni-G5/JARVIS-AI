from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import tempfile
from datetime import datetime

app = FastAPI(title="JARVIS STT Service", version="0.1.0")

class TranscriptResponse(BaseModel):
    text: str
    confidence: float
    language: str
    duration: float
    timestamp: str

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "stt", "model": "whisper.cpp"}

@app.post("/transcribe", response_model=TranscriptResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcrit un fichier audio en texte.
    TODO: Intégrer whisper.cpp ou faster-whisper
    """
    try:
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # TODO: Appeler whisper.cpp pour transcription
        # Pour l'instant, placeholder
        
        os.unlink(tmp_path)
        
        return TranscriptResponse(
            text="Transcription en cours d'implémentation",
            confidence=0.95,
            language="fr",
            duration=0.0,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)