# Bridge API - Gateway JARVIS

Point d'entrée principal pour tous les clients (web, mobile, AR).

## Endpoints

### POST /command
Traite une commande texte.
```json
{
  "user_id": "user-123",
  "text": "Allume les lumières du salon",
  "context": []
}
```

### WebSocket /voice/stream
Streaming audio bidirectionnel pour commandes vocales.

### POST /vision/upload
Upload d'images/vidéos pour analyse.

### GET /status
Status de tous les services connectés.

### GET /health
Health check du bridge.

## Variables d'environnement
- `STT_HOST` : host:port du service STT
- `TTS_HOST` : host:port du service TTS  
- `LLM_HOST` : host:port du LLM agent
- `VISION_HOST` : host:port du service Vision

## Lancement
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```