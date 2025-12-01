# LLM Agent - Core Intelligence

Module central de JARVIS responsable de la planification, raisonnement et orchestration des autres modules.

## Architecture
- Utilise le system prompt `prompts/system_jarvis_fr.txt`
- Template utilisateur dans `prompts/user_template.txt`
- Endpoint principal : `POST /think`
- Intégration mémoire vectorielle (Chroma)
- Appels tools vers : STT, TTS, Vision, Action Exec, Memory, IoT

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## Variables d'environnement
- `LLM_MODEL_PATH` : chemin vers le modèle local (Llama)
- `CHROMA_URL` : URL du service de mémoire vectorielle
- `MAX_TOKENS` : limite de tokens par réponse (défaut: 2048)
- `TEMPERATURE` : créativité du modèle (défaut: 0.7)