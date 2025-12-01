#!/bin/bash

# Démarrage rapide en mode développement (tous services en local)

echo "🚀 Démarrage JARVIS en mode dev..."

# Activer venv si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Démarrer ChromaDB en background (si Docker dispo)
if command -v docker &> /dev/null; then
    echo "Starting ChromaDB..."
    docker run -d --name jarvis-chroma -p 8008:8000 ghcr.io/chroma-core/chroma:latest || true
fi

# Lancer chaque service en background
cd apps/bridge_api && uvicorn main:app --port 8000 --reload &
cd apps/llm_agent && uvicorn main:app --port 9000 --reload &
cd apps/stt && uvicorn main:app --port 5000 --reload &
cd apps/tts && uvicorn main:app --port 7000 --reload &
cd apps/vision && uvicorn main:app --port 8002 --reload &
cd apps/memory && uvicorn main:app --port 8003 --reload &
cd apps/action_exec && uvicorn main:app --port 8001 --reload &

echo ""
echo "✅ Services lancés en arrière-plan"
echo "Bridge API: http://localhost:8000/docs"
echo ""
echo "Pour arrêter: pkill -f uvicorn"

wait