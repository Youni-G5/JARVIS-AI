from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

app = FastAPI(title="JARVIS Bridge API", version="0.1.0")

# CORS pour frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration services
STT_HOST = os.getenv("STT_HOST", "localhost:5000")
TTS_HOST = os.getenv("TTS_HOST", "localhost:7000")
LLM_HOST = os.getenv("LLM_HOST", "localhost:9000")
VISION_HOST = os.getenv("VISION_HOST", "localhost:8001")

class CommandRequest(BaseModel):
    user_id: str
    text: str
    context: Optional[list] = []

class CommandResponse(BaseModel):
    response_text: str
    audio_url: Optional[str] = None
    actions: Optional[list] = []

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "bridge_api",
        "timestamp": datetime.utcnow().isoformat(),
        "connected_services": {
            "stt": STT_HOST,
            "tts": TTS_HOST,
            "llm": LLM_HOST,
            "vision": VISION_HOST
        }
    }

@app.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Traite une commande texte et retourne la réponse de JARVIS.
    Workflow: text -> LLM -> actions -> TTS -> response
    """
    try:
        # Appel au LLM agent
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{LLM_HOST}/think",
                json={
                    "user_id": request.user_id,
                    "input": request.text,
                    "context": request.context,
                    "tools": ["action_exec", "memory", "notify"]
                }
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=500, detail="LLM service error")
                llm_response = await resp.json()
        
        # TODO: Exécuter tool_calls si nécessaire
        # TODO: Générer audio via TTS
        
        return CommandResponse(
            response_text=llm_response.get("explanation", "Commande reçue."),
            actions=llm_response.get("tool_calls", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/voice/stream")
async def voice_stream(websocket: WebSocket):
    """
    Websocket pour streaming audio bidirectionnel.
    Client envoie audio -> STT -> LLM -> TTS -> Client reçoit audio
    """
    await websocket.accept()
    try:
        while True:
            # Reçoit chunks audio du client
            audio_data = await websocket.receive_bytes()
            
            # TODO: Envoyer à STT service
            # TODO: Traiter avec LLM
            # TODO: Générer réponse TTS
            # TODO: Streamer audio au client
            
            await websocket.send_json({
                "status": "processing",
                "message": "Audio reçu, traitement en cours..."
            })
    
    except WebSocketDisconnect:
        print("Client disconnected from voice stream")

@app.post("/vision/upload")
async def upload_vision(file: UploadFile = File(...), user_id: str = "default"):
    """
    Upload d'image ou vidéo pour analyse Vision.
    """
    try:
        contents = await file.read()
        
        # TODO: Envoyer au service Vision
        # TODO: Retourner objets détectés, texte OCR, etc.
        
        return {
            "status": "received",
            "filename": file.filename,
            "size": len(contents),
            "analysis": "Vision service en cours d'implémentation"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Status complet de tous les services connectés."""
    services_status = {}
    
    # Test connexion à chaque service
    services = {
        "llm": f"http://{LLM_HOST}/health",
        # "stt": f"http://{STT_HOST}/health",
        # "tts": f"http://{TTS_HOST}/health",
        # "vision": f"http://{VISION_HOST}/health"
    }
    
    async with aiohttp.ClientSession() as session:
        for name, url in services.items():
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    services_status[name] = "healthy" if resp.status == 200 else "unhealthy"
            except:
                services_status[name] = "unreachable"
    
    return {
        "bridge": "healthy",
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "JARVIS Bridge API - Gateway to AI Assistant",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)