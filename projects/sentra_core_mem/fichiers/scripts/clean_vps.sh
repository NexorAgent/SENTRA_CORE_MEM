#!/bin/bash

# Nettoyage complet Docker
printf "\n🧼 Nettoyage Docker en cours...\n"
docker system prune -a -f

echo "🧼 Suppression des volumes non utilisés..."
docker volume prune -f

# Nettoyage du cache APT
printf "\n🧼 Nettoyage cache apt...\n"
sudo apt autoremove -y && sudo apt clean

echo "✅ Nettoyage terminé à $(date)"