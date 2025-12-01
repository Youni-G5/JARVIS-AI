# 🤖 JARVIS — Assistant Personnel IA Local & Sécurisé

[![CI](https://github.com/Youni-G5/JARVIS-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/Youni-G5/JARVIS-AI/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> Assistant personnel multiplateforme avec IA, conçu pour fonctionner 100% en local avec confidentialité, modularité et sécurité au cœur du système.

## ✨ Fonctionnalités

- 🎤 **Commandes vocales** - Reconnaissance vocale (Whisper) et synthèse (Coqui TTS)
- 🧠 **Raisonnement IA** - LLM local (Llama 3.1) pour planification et décisions
- 👁️ **Vision** - Détection objets (YOLO), OCR et reconnaissance faciale
- 💾 **Mémoire contextuelle** - Base vectorielle (ChromaDB) pour continuité des conversations
- ⚙️ **Actions OS** - Exécution sécurisée de commandes avec sandboxing et audit
- 🟢 **IoT/Domotique** - Intégration Home Assistant et MQTT (en développement)
- 🔒 **Privacy-first** - Toutes les données restent locales par défaut
- 🎯 **Modulaire** - Architecture microservices facile à étendre

## 📚 Table des matières

- [Installation Rapide](#-installation-rapide)
- [Architecture](#-architecture)
- [Utilisation](#-utilisation)
- [Développement](#-développement)
- [Roadmap](#-roadmap)
- [Contribution](#-contribution)

## 🚀 Installation Rapide

### Prérequis

- Python 3.11+
- Docker & Docker Compose (recommandé)
- Node.js 18+ (pour frontend web)
- 8GB RAM minimum (16GB recommandé pour LLM)

### Installation automatique

```bash
# Cloner le repository
git clone https://github.com/Youni-G5/JARVIS-AI.git
cd JARVIS-AI

# Exécuter le script d'installation
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Démarrage avec Docker

```bash
# Démarrer tous les services
docker-compose -f infra/docker-compose.yml up --build

# Accéder à l'interface
# Bridge API: http://localhost:8000/docs
# Web UI: http://localhost:3000
```

### Démarrage manuel (développement)

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer les services individuellement
cd apps/bridge_api && uvicorn main:app --port 8000 --reload &
cd apps/llm_agent && uvicorn main:app --port 9000 --reload &
cd apps/stt && uvicorn main:app --port 5000 --reload &
# ... autres services

# Lancer le frontend web
cd frontend/web_ui
npm install
npm start
```

## 🏛️ Architecture

```
┌───────────────────┐
│  Client Devices  │
│ (Web/Mobile/AR) │
└───────┬───────────┘
        │
        │ WebSocket/HTTP
        │
┌───────┴───────────┐
│   Bridge API     │ (Port 8000)
│   FastAPI        │
└───────┬───────────┘
        │
        ├──────────────────────────────┐
        │                               │
┌───────┴───────┐     ┌───────────┴──────┐
│  LLM Agent    │     │   Services      │
│  (Llama 3.1)  │     │   Modules       │
│  Port 9000    │     ├──────────────────┤
└────────────────┘     │ STT (5000)     │
                      │ TTS (7000)     │
                      │ Vision (8002)  │
                      │ Memory (8003)  │
                      │ Action (8001)  │
                      └──────────────────┘
```

### Modules principaux

| Module | Port | Description |
|--------|------|-------------|
| **Bridge API** | 8000 | Gateway principal, orchestration |
| **LLM Agent** | 9000 | Raisonnement, planification (Llama) |
| **STT** | 5000 | Speech-to-Text (Whisper) |
| **TTS** | 7000 | Text-to-Speech (Coqui) |
| **Vision** | 8002 | Computer vision (YOLO, OCR) |
| **Memory** | 8003 | Mémoire vectorielle (ChromaDB) |
| **Action Exec** | 8001 | Exécution sécurisée commandes |

Consultez [docs/architecture.md](docs/architecture.md) pour plus de détails.

## 💻 Utilisation

### Interface Web

1. Accédez à http://localhost:3000
2. Tapez une commande ou utilisez le micro pour la voix
3. JARVIS traite et répond avec actions si nécessaire

### API REST

```bash
# Envoyer une commande texte
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "text": "Quelle heure est-il ?",
    "context": []
  }'

# Vérifier le status de tous les services
curl http://localhost:8000/status
```

### WebSocket (Streaming vocal)

```javascript
const ws = new WebSocket('ws://localhost:8000/voice/stream');
ws.onopen = () => {
  // Envoyer chunks audio
  ws.send(audioData);
};
```

## 🛠️ Développement

### Structure du projet

```
jarvis/
├── apps/              # Microservices
│   ├── bridge_api/
│   ├── llm_agent/
│   ├── stt/
│   ├── tts/
│   ├── vision/
│   ├── memory/
│   └── action_exec/
├── frontend/         # Interfaces utilisateur
│   ├── web_ui/
│   └── flutter_app/
├── infra/            # Docker, nginx
├── docs/             # Documentation
├── scripts/          # Scripts utilitaires
└── tests/            # Tests unitaires
```

### Ajouter un nouveau module

1. Créer dossier dans `apps/mon_module/`
2. Ajouter `main.py`, `requirements.txt`, `Dockerfile`
3. Exposer endpoints FastAPI avec `/health`
4. Mettre à jour `docker-compose.yml`
5. Documenter dans `apps/mon_module/README.md`

### Tests

```bash
# Lancer les tests unitaires
pytest tests/

# Tester tous les services
./scripts/test_services.sh

# Lint et formatting
flake8 apps/
black apps/
isort apps/
```

## 🛣️ Roadmap

### Phase 1 - MVP (Semaines 1-6) ✅
- [x] Architecture de base et squelette
- [x] Modules core (Bridge, LLM, STT, TTS, Vision, Memory, Actions)
- [x] Frontend web minimal
- [x] Docker Compose orchestration
- [x] CI/CD basique

### Phase 2 - Implémentation fonctionnelle (Semaines 7-12) 🔄
- [ ] [Intégrer LLM local Llama](https://github.com/Youni-G5/JARVIS-AI/issues/1)
- [ ] [Whisper STT complet](https://github.com/Youni-G5/JARVIS-AI/issues/2)
- [ ] [Coqui TTS avec voix personnalisée](https://github.com/Youni-G5/JARVIS-AI/issues/3)
- [ ] [Vision complète (YOLO + OCR)](https://github.com/Youni-G5/JARVIS-AI/issues/4)
- [ ] [Mémoire vectorielle finale](https://github.com/Youni-G5/JARVIS-AI/issues/5)

### Phase 3 - IoT & Extensions (Semaines 13-16)
- [ ] [Home Assistant + MQTT](https://github.com/Youni-G5/JARVIS-AI/issues/6)
- [ ] App mobile Flutter
- [ ] Plugins marketplace
- [ ] Optimisations performance

### Phase 4 - Avancé (Long terme)
- [ ] Support AR/VR
- [ ] Multi-utilisateurs
- [ ] Apprentissage personnalisé
- [ ] Extensions cloud optionnelles

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

### Comment contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 🔒 Sécurité & Privacy

- **Local-first** : Données sensibles ne quittent jamais votre machine
- **Sandboxing** : Commandes exécutées dans environnement contrôlé
- **Audit logs** : Toutes les actions sont tracées
- **Chiffrement** : Secrets stockés chiffrés (AES-256)
- **Consentement** : Permissions explicites pour caméra/micro

Consultez [docs/security.md](docs/security.md) pour plus d'informations.

## 📝 Documentation

- [Architecture détaillée](docs/architecture.md)
- [Spécification API](docs/api_spec.md)
- [Guide sécurité](docs/security.md)
- [Guide contribution](CONTRIBUTING.md)

## 📜 License

Ce projet est sous licence MIT - voir [LICENSE](LICENSE) pour détails.

## 👥 Auteurs

- **Youni-G5** - *Créateur et mainteneur principal*

## 🚀 Support

- 🐛 [Issues GitHub](https://github.com/Youni-G5/JARVIS-AI/issues)
- 💬 [Discussions](https://github.com/Youni-G5/JARVIS-AI/discussions)

---

<p align="center">
  <strong>JARVIS</strong> - Votre assistant IA personnel, privé et puissant 🤖
</p>
<p align="center">
  Conçu avec ❤️ pour la communauté open-source
</p>