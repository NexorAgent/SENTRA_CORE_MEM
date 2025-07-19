# Notice Sauvegarde SENTRA_CORE_MEM

## But : 
Expliquer et industrialiser la procédure de sauvegarde automatisée du projet SENTRA_CORE_MEM (fichiers, dossiers, logs, configs, scripts, snapshots VPS, upload cloud).

- Script Bash fourni
- Exemple de ligne CRON
- Conseils pour tests et vérifications
- Exclusion et encryption facultative

**Notice à lire avant toute modification structurelle ou restauration.**

## Script fourni
Le fichier `backup/backup_sentra_core.sh` réalise automatiquement :
1. La compression de `/home/debian` et `/srv`.
2. L’export des volumes et images Docker.
3. L’upload via `rclone` vers Google Drive (`sentra_backup`).
4. Une notification Discord en fin de tâche.

### Exemple CRON
```
0 3 * * * /home/debian/SENTRA_CORE_MEM/backup/backup_sentra_core.sh
```

### Restauration conseillée
1. Recréez un VPS Debian propre.
2. Téléchargez le dossier backup depuis Google Drive.
3. Décompressez volumes et images Docker (`docker load` puis extraction tar`).
4. Exécutez `docker compose up -d` pour relancer les services.

Testez toujours la procédure sur une instance de développement avant toute récupération définitive.
