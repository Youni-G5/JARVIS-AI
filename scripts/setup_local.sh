#!/bin/bash

# Script d'installation automatique JARVIS
# Usage: ./scripts/setup_local.sh

set -e

echo "=== Installation JARVIS - Assistant IA Local ==="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ requis. Veuillez l'installer."
    exit 1
fi

echo "✅ Python détecté: $(python3 --version)"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker non détecté. Installation manuelle nécessaire pour certains services."
else
    echo "✅ Docker détecté: $(docker --version)"
fi

# Créer environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances pour chaque service
echo ""
echo "📥 Installation des dépendances..."

for service in bridge_api llm_agent stt tts vision memory action_exec; do
    if [ -f "apps/$service/requirements.txt" ]; then
        echo "  - Installation $service..."
        pip install -q -r "apps/$service/requirements.txt"
    fi
done

echo "✅ Dépendances installées"

# Copier .env.example vers .env
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  Veuillez configurer les variables dans .env"
fi

# Télécharger modèles (optionnel)
echo ""
echo "🤖 Modèles IA (optionnel):"
echo "  - LLM: Téléchargez Llama via Ollama (ollama pull llama3.1)"
echo "  - STT: Whisper sera téléchargé automatiquement au premier usage"
echo "  - Vision: YOLOv8 sera téléchargé automatiquement"

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour démarrer JARVIS:"
echo "  1. Configurez .env avec vos paramètres"
echo "  2. docker-compose -f infra/docker-compose.yml up"
echo "  OU lancez manuellement chaque service:"
echo "     - cd apps/bridge_api && uvicorn main:app --port 8000"
echo "     - cd apps/llm_agent && uvicorn main:app --port 9000"
echo "     - etc."
echo ""
echo "Interface web: cd frontend/web_ui && npm install && npm start"
echo ""