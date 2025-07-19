#!/bin/bash

# Vérifie et inscrit le cron hebdomadaire pour nettoyage VPS
CRON_LINE="0 4 * * 0 /home/debian/SENTRA_CORE_MEM/fichiers/scripts/clean_vps.sh >> /var/log/clean_vps.log 2>&1"
(crontab -l | grep -v -F "$CRON_LINE"; echo "$CRON_LINE") | crontab -

echo "✅ Tâche cron ajoutée : $CRON_LINE"