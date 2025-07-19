#!/bin/bash

DATE=$(date +%F)
BACKUP_DIR="/home/debian/backup_local/sentra_core_backups"
VOLUME_DIR="$BACKUP_DIR/volumes"
CODE_DIR="$BACKUP_DIR/code"

mkdir -p "$VOLUME_DIR"
mkdir -p "$CODE_DIR"

echo "🔹 Sauvegarde du /home/debian..."
tar czf "$CODE_DIR/home_debian_$DATE.tar.gz" /home/debian

echo "🔹 Sauvegarde du /srv/..."
tar czf "$CODE_DIR/srv_$DATE.tar.gz" /srv

echo "🔹 Sauvegarde des volumes Docker..."
for VOLUME in $(docker volume ls -q); do
  docker run --rm -v $VOLUME:/volume -v "$VOLUME_DIR":/backup alpine \
    tar czf /backup/${VOLUME}_$DATE.tar.gz -C /volume .
done

echo "🔹 Sauvegarde des images Docker..."
IMAGES=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>')
if [ -n "$IMAGES" ]; then
  docker save -o "$BACKUP_DIR/docker_images_$DATE.tar" $IMAGES
fi

echo "🔹 Upload vers Google Drive..."
rclone copy "$BACKUP_DIR" "drive vps backup:sentra_backup"

echo "✅ Sauvegarde complète terminée : $DATE"

# Notification Discord
WEBHOOK_URL="https://discord.com/api/webhooks/1395995681948303411/e8FCy7fHeQC1BcogjzAhEqpEYfMUTROJitGMVKRx1m7BcXEHZZ9AMJNg1qXyQ4bcyVPm"
HOSTNAME=$(hostname)
MESSAGE="✅ Sauvegarde SENTRA_CORE terminée avec succès sur \`$HOSTNAME\` le $(date)"

curl -H "Content-Type: application/json" \
     -X POST \
     -d "{\"content\": \"$MESSAGE\"}" \
     "$WEBHOOK_URL"


