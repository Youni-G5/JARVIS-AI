# JARVIS — Assistant Personnel Local, Sécurisé & IA

## Introduction
JARVIS est un assistant personnel multiplateforme conçu pour tourner localement tout en exploitant des technologies open source d’IA pour la voix, la vision, la planification et l'automatisation. Il privilégie la confidentialité, la modularité (plugins), la sécurité et la possibilité d'extension sur le cloud (en option).

- **Local-first** : données sensibles hébergées localement
- **Pluri-modules** : voix, vision, actions OS/IoT, mémoire vectorielle, planification
- **Open-source** : stack Python, FastAPI, Llama, Whisper, Coqui, YOLO, etc.

## Fonctionnalités (MVP)
- Commande vocale, texte ou API web
- Planification de tâches, gestion mémoire contextuelle
- Actions OS + IoT sécurisées (sandbox, audit log)
- Extensions faciles via modules
- Frontends Flutter/React en local

Consultez `docs/` pour l’architecture, la sécurité, l’API et le détail modules.