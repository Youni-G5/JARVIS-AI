#!/bin/bash

# Script de test rapide de tous les services JARVIS

echo "=== Test des services JARVIS ==="
echo ""

services=(
    "bridge_api:8000"
    "llm_agent:9000"
    "stt:5000"
    "tts:7000"
    "vision:8002"
    "memory:8003"
    "action_exec:8001"
)

for service_port in "${services[@]}"; do
    IFS=':' read -r service port <<< "$service_port"
    echo -n "Testing $service (port $port)... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ FAIL (HTTP $response)"
    fi
done

echo ""
echo "Test terminé."