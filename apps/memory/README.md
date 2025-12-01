# Memory Service - Vector Memory Store

Service de mémoire à long terme utilisant ChromaDB pour stockage vectoriel et recherche sémantique.

## Fonctionnalités
- Stockage de souvenirs avec embeddings automatiques
- Recherche sémantique (top-k similarity)
- Filtrage par type (préférence, fait, événement, rappel)
- Expiration automatique (TTL)
- Compliance GDPR (suppression utilisateur)

## Endpoints
- POST /write - Stocker un souvenir
- POST /query - Recherche sémantique
- DELETE /clear/{user_id} - Effacer mémoire utilisateur
- GET /stats - Statistiques

## Variables d'environnement
- CHROMA_HOST - Hôte ChromaDB (défaut: localhost)
- CHROMA_PORT - Port ChromaDB (défaut: 8008)