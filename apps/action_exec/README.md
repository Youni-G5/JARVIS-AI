# Action Exec - Sandboxed Command Execution

Service d'exécution sécurisée de commandes système avec audit logging.

## Sécurité
- Détection commandes dangereuses
- Mode dry-run par défaut
- Timeout configurable
- Hash de transaction pour audit
- Sudo bloqué sans confirmation

## Endpoint
POST /run - Exécute une commande
```json
{
  "cmd": "echo 'Hello JARVIS'",
  "dry_run": false,
  "timeout": 30
}
```