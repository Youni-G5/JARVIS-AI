from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional
import io
import os
from datetime import datetime
from tts_engine import TTSEngine

app = FastAPI(title="JARVIS TTS Service", version="0.2.0")

# Initialiser TTS
model_name = os.getenv("TTS_MODEL", "tts_models/fr/css10/vits")
gpu = os.getenv("TTS_GPU", "false").lower() == "true"

tts_engine = TTSEngine(model_name=model_name, gpu=gpu)

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "jarvis_fr"
    speed: float = 1.0
    language: str = "fr"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "tts",
        "engine": "coqui-tts",
        "model": model_name,
        "tts_loaded": tts_engine.tts is not None
    }

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Synthétise du texte en audio.
    Retourne un fichier WAV en streaming.
    """
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(request.text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Text too long (max 5000 characters)"
        )
    
    try:
        # Vérifier si voix personnalisée
        voices = tts_engine.get_available_voices()
        selected_voice = next((v for v in voices if v["id"] == request.voice), None)
        
        if selected_voice and selected_voice.get("type") == "custom":
            # Voice cloning
            audio_data = tts_engine.synthesize_with_voice_cloning(
                text=request.text,
                reference_audio_path=selected_voice["path"],
                language=request.language
            )
        else:
            # Synthèse normale
            audio_data = tts_engine.synthesize(
                text=request.text,
                language=request.language,
                speed=request.speed
            )
        
        if audio_data is None:
            raise HTTPException(
                status_code=500,
                detail="TTS synthesis failed"
            )
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="jarvis_speech_{datetime.utcnow().timestamp()}.wav"'
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize/stream")
async def synthesize_stream(text: str = Form(...), language: str = Form("fr")):
    """
    Synthèse avec streaming pour réponses longues.
    """
    try:
        # Pour l'instant, même implémentation que synthesize
        # TODO: Implémenter vrai streaming avec chunks
        audio_data = tts_engine.synthesize(text, language=language)
        
        if audio_data is None:
            raise HTTPException(status_code=500, detail="TTS failed")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def list_voices():
    """Liste des voix disponibles."""
    return {
        "voices": tts_engine.get_available_voices()
    }

@app.post("/voices/add")
async def add_custom_voice(
    voice_name: str = Form(...),
    audio_sample: UploadFile = File(...)
):
    """
    Ajoute une voix personnalisée pour voice cloning.
    Envoyer un sample audio WAV de 5-10 secondes.
    """
    try:
        # Créer dossier custom_voices si n'existe pas
        custom_voices_dir = os.getenv("CUSTOM_VOICES_DIR", "./custom_voices")
        os.makedirs(custom_voices_dir, exist_ok=True)
        
        # Sauvegarder le fichier
        voice_path = os.path.join(custom_voices_dir, f"{voice_name}.wav")
        contents = await audio_sample.read()
        
        with open(voice_path, 'wb') as f:
            f.write(contents)
        
        return {
            "status": "success",
            "voice_id": voice_name,
            "message": f"Voice '{voice_name}' added successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """Liste des modèles TTS disponibles."""
    if tts_engine.available_models:
        return {
            "models": tts_engine.available_models[:20],  # Limiter pour performance
            "current": model_name
        }
    else:
        return {
            "models": [],
            "current": model_name,
            "note": "TTS not initialized or models list unavailable"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)