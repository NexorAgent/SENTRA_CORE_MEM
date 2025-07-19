#!/bin/bash
# 📦 Script de sauvegarde SENTRA_CORE_MEM vers Google Drive
# Exécute tous les jours à minuit via cron

LOGFILE="/var/log/backup_sentra.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Commande de sauvegarde (à adapter selon le nom de remote)
echo "$DATE - Démarrage de la sauvegarde..." >> $LOGFILE
rclone copy -v /home/debian/SENTRA_CORE_MEM "drive vps backup:sentra_backup" >> $LOGFILE 2>&1
echo "$DATE - Sauvegarde terminée." >> $LOGFILE
