# STT Service - Speech to Text

Service de transcription audio vers texte utilisant Whisper (faster-whisper ou whisper.cpp).

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
uvicorn main:app --port 5000
```

## Endpoint
POST /transcribe - Upload fichier audio, retourne transcription + métadonnées