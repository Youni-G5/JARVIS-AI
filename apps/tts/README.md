# TTS Service - Text to Speech

Service de synthèse vocale utilisant Coqui TTS ou Piper.

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
uvicorn main:app --port 7000
```

## Endpoints
- POST /synthesize - Génère audio depuis texte
- GET /voices - Liste des voix disponibles