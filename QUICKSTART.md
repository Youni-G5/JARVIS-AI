# 🚀 JARVIS - Guide de Démarrage Rapide

Guide pour lancer JARVIS en moins de 10 minutes.

## 💻 Prérequis

- **Docker** & **Docker Compose** (recommandé)
- **Python 3.11+** (pour installation manuelle)
- **8GB RAM minimum** (16GB recommandé pour LLM)
- **10-30GB espace disque** (pour modèles IA)

## ⚡ Installation Express avec Docker

### 1. Cloner le projet

```bash
git clone https://github.com/Youni-G5/JARVIS-AI.git
cd JARVIS-AI
```

### 2. Configurer l'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env (optionnel pour démarrage rapide)
nano .env
```

### 3. Lancer tous les services

```bash
cd infra
docker-compose up --build
```

⏳ **Première exécution** : 5-10 minutes (téléchargement modèles)

### 4. Vérifier que tout fonctionne

Dans un autre terminal :

```bash
# Tester le Bridge API
curl http://localhost:8000/health

# Tester tous les services
./scripts/test_services.sh
```

### 5. Accéder à l'interface

- **API Documentation** : http://localhost:8000/docs
- **Interface Web** : http://localhost:3000 (si frontend lancé)

## 🗣️ Test Rapide

### Commande texte (via API)

```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "text": "Bonjour JARVIS, quelle heure est-il ?",
    "context": []
  }'
```

### Test STT (transcription audio)

```bash
curl -X POST http://localhost:5000/transcribe \
  -F "audio=@test_audio.wav"
```

### Test TTS (synthèse vocale)

```bash
curl -X POST http://localhost:7000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour, je suis JARVIS", "language": "fr"}' \
  --output jarvis_voice.wav
```

### Test Vision (analyse image)

```bash
curl -X POST http://localhost:8002/analyze \
  -F "file=@test_image.jpg" \
  -F "detect_objects=true" \
  -F "detect_text=true"
```

## 🐛 Dépannage Rapide

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs -f

# Redémarrer un service spécifique
docker-compose restart llm_agent
```

### Erreur "model not found"

Les modèles sont téléchargés automatiquement au premier lancement. Patientez quelques minutes.

### Port déjà utilisé

```bash
# Modifier les ports dans infra/docker-compose.yml
# Exemple : changer 8000:8000 en 8080:8000
```

### Manque de mémoire

```bash
# Utiliser modèles plus légers dans .env
WHISPER_MODEL_SIZE=tiny
YOLO_MODEL=yolov8n.pt
```

## 🎯 Prochaines étapes

1. **Frontend Web** : Lancer l'interface React
   ```bash
   cd frontend/web_ui
   npm install
   npm start
   ```

2. **Personnaliser JARVIS** :
   - Modifier les prompts dans `apps/llm_agent/prompts/`
   - Ajouter voix personnalisée dans TTS
   - Configurer Home Assistant pour IoT

3. **Développement** :
   - Consulter [CONTRIBUTING.md](CONTRIBUTING.md)
   - Voir les [issues ouvertes](https://github.com/Youni-G5/JARVIS-AI/issues)
   - Lire la [documentation complète](docs/)

## 📚 Ressources

- [README principal](README.md)
- [Architecture détaillée](docs/architecture.md)
- [API Specification](docs/api_spec.md)
- [Guide sécurité](docs/security.md)

## 👥 Support

Problème ? Questions ?

- 🐛 [Signaler un bug](https://github.com/Youni-G5/JARVIS-AI/issues/new)
- 💬 [Discussions](https://github.com/Youni-G5/JARVIS-AI/discussions)

---

**Bon usage de JARVIS !** 🤖