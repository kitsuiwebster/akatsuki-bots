#!/bin/bash

echo "🔴 Démarrage du système Akatsuki..."

docker-compose up --build -d

echo "✅ Système démarré!"
echo ""
echo "📊 Portainer: http://localhost:9000"
echo "📝 Logs: docker-compose logs -f"
echo "🛑 Arrêter: docker-compose down"