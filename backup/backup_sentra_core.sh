# Écriture d'un script bash valide pour les sauvegardes
script_content = """#!/bin/bash

DATE=$(date +%F)
BACKUP_DIR="/mnt/backup/sentra_core_backups"
VOLUME_DIR="$BACKUP_DIR/volumes"

mkdir -p "$VOLUME_DIR"

echo "??? Sauvegarde du code..."
tar czf "$BACKUP_DIR/sentra_core_code_$DATE.tar.gz" ~/SENTRA_CORE_MEM

echo "?? Sauvegarde des volumes Docker..."
for VOLUME in $(docker volume ls -q); do
  docker run --rm -v $VOLUME:/volume -v "$VOLUME_DIR":/backup alpine \\
    tar czf /backup/${VOLUME}_$DATE.tar.gz -C /volume .
done

echo "?? Sauvegarde des images Docker..."
docker save -o "$BACKUP_DIR/sentra_core_images_$DATE.tar" \\
  $(docker images --format '{{.Repository}}:{{.Tag}}' | grep sentra_core)

echo "? Sauvegarde terminée : $DATE"
"""

# Sauvegarde du script prêt à télécharger
with open("/mnt/data/backup_sentra_core_fixed.sh", "w") as f:
    f.write(script_content)

"/mnt/data/backup_sentra_core_fixed.sh"
