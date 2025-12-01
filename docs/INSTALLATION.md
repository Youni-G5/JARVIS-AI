# Guide d'Installation Détaillé JARVIS

Guide complet pour installer JARVIS selon différentes configurations.

## Table des matières

1. [Installation avec Docker](#installation-docker)
2. [Installation manuelle](#installation-manuelle)
3. [Configuration des modèles IA](#configuration-modèles)
4. [Frontend](#frontend)
5. [Optimisations](#optimisations)

---

## Installation Docker

### Prérequis

```bash
# Vérifier Docker
docker --version  # Min 20.10+
docker-compose --version  # Min 1.29+
```

### Installation standard

```bash
git clone https://github.com/Youni-G5/JARVIS-AI.git
cd JARVIS-AI

# Configuration
cp .env.example .env

# Lancer
cd infra
docker-compose up -d

# Vérifier
docker-compose ps
```

### Commandes utiles Docker

```bash
# Voir les logs
docker-compose logs -f llm_agent

# Redémarrer un service
docker-compose restart stt

# Arrêter tout
docker-compose down

# Arrêter et supprimer volumes
docker-compose down -v

# Rebuild après modification
docker-compose up --build llm_agent
```

---

## Installation Manuelle

### 1. Prérequis système

**Ubuntu/Debian** :
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
                    ffmpeg tesseract-ocr tesseract-ocr-fra \
                    libsndfile1 libgl1-mesa-glx libglib2.0-0
```

**macOS** :
```bash
brew install python@3.11 ffmpeg tesseract tesseract-lang
```

**Windows** :
- Installer Python 3.11 depuis python.org
- Installer FFmpeg depuis ffmpeg.org
- Installer Tesseract depuis github.com/UB-Mannheim/tesseract/wiki

### 2. Installation Python

```bash
# Cloner
git clone https://github.com/Youni-G5/JARVIS-AI.git
cd JARVIS-AI

# Environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installation des dépendances
./scripts/setup_local.sh

# Ou manuellement pour chaque service
pip install -r apps/bridge_api/requirements.txt
pip install -r apps/llm_agent/requirements.txt
pip install -r apps/stt/requirements.txt
pip install -r apps/tts/requirements.txt
pip install -r apps/vision/requirements.txt
pip install -r apps/memory/requirements.txt
pip install -r apps/action_exec/requirements.txt
```

### 3. Lancer les services manuellement

**Terminal 1 - ChromaDB** :
```bash
docker run -p 8008:8000 ghcr.io/chroma-core/chroma:latest
```

**Terminal 2 - Bridge API** :
```bash
cd apps/bridge_api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 - LLM Agent** :
```bash
cd apps/llm_agent
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

**Terminal 4 - STT** :
```bash
cd apps/stt
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

**Terminal 5 - TTS** :
```bash
cd apps/tts
uvicorn main:app --host 0.0.0.0 --port 7000 --reload
```

**Terminal 6 - Vision** :
```bash
cd apps/vision
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 7 - Memory** :
```bash
cd apps/memory
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 8 - Action Exec** :
```bash
cd apps/action_exec
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Ou utiliser le script** :
```bash
./scripts/start_dev.sh
```

---

## Configuration Modèles

### LLM (Llama)

**Option 1 - Via Ollama (recommandé)** :
```bash
# Installer Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Télécharger Llama
ollama pull llama3.1

# Le modèle sera dans ~/.ollama/models
```

**Option 2 - Téléchargement manuel** :
```bash
# Télécharger depuis Hugging Face
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

# Placer dans le dossier modèles
mkdir -p models
mv llama-2-7b-chat.Q4_K_M.gguf models/

# Configurer dans .env
LLM_MODEL_PATH=./models/llama-2-7b-chat.Q4_K_M.gguf
```

### Whisper (STT)

Les modèles sont téléchargés automatiquement au premier usage.

Pour pré-télécharger :
```bash
python -c "from faster_whisper import WhisperModel; WhisperModel('base')"
```

Tailles disponibles :
- `tiny` : 75 MB, rapide, précision moyenne
- `base` : 142 MB, **recommandé** pour début
- `small` : 466 MB, bonne précision
- `medium` : 1.5 GB, excellente précision
- `large` : 2.9 GB, meilleure précision

### TTS (Coqui)

Modèles téléchargés automatiquement.

Lister modèles disponibles :
```bash
tts --list_models
```

Modèles recommandés :
- FR : `tts_models/fr/css10/vits`
- EN : `tts_models/en/ljspeech/tacotron2-DDC`
- Multilingual + cloning : `tts_models/multilingual/multi-dataset/xtts_v2`

### YOLO (Vision)

Téléchargé automatiquement au premier usage.

Modèles disponibles :
- `yolov8n.pt` : Nano, très rapide
- `yolov8s.pt` : Small, **recommandé**
- `yolov8m.pt` : Medium, bonne précision
- `yolov8l.pt` : Large, excellente précision

---

## Frontend

### Interface Web React

```bash
cd frontend/web_ui

# Installation
npm install

# Configuration
echo "REACT_APP_BRIDGE_API=http://localhost:8000" > .env.local

# Lancement
npm start

# Build production
npm run build
```

Accès : http://localhost:3000

---

## Optimisations

### Pour machines limitées (4-8GB RAM)

```bash
# .env
WHISPER_MODEL_SIZE=tiny
YOLO_MODEL=yolov8n.pt
WHISPER_COMPUTE_TYPE=int8

# Utiliser Llama 7B quantizé en 4-bit
LLM_MODEL_PATH=./models/llama-2-7b-chat.Q4_K_S.gguf
```

### Pour machines puissantes (16GB+ RAM, GPU)

```bash
# .env
WHISPER_MODEL_SIZE=large
YOLO_MODEL=yolov8l.pt
WHISPER_DEVICE=cuda
TTS_GPU=true

# Utiliser Llama 13B ou 70B
LLM_MODEL_PATH=./models/llama-2-13b-chat.Q5_K_M.gguf
```

### GPU NVIDIA

```bash
# Installer CUDA toolkit
# https://developer.nvidia.com/cuda-downloads

# Installer PyTorch avec CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Vérifier
python -c "import torch; print(torch.cuda.is_available())"
```

---

## Vérification Installation

```bash
# Tester tous les services
./scripts/test_services.sh

# Vérifier health de chaque service
curl http://localhost:8000/health  # Bridge
curl http://localhost:9000/health  # LLM
curl http://localhost:5000/health  # STT
curl http://localhost:7000/health  # TTS
curl http://localhost:8002/health  # Vision
curl http://localhost:8003/health  # Memory
curl http://localhost:8001/health  # Action
```

---

## Support

Problèmes d'installation ?

1. Consulter [QUICKSTART.md](../QUICKSTART.md) pour dépannage rapide
2. Voir les [issues existantes](https://github.com/Youni-G5/JARVIS-AI/issues)
3. Créer une [nouvelle issue](https://github.com/Youni-G5/JARVIS-AI/issues/new)