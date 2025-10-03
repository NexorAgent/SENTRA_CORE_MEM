# Manuel de déploiement – VPS OVH (Debian 12)

Ce guide pas à pas prépare un VPS OVH Debian 12 pour héberger SENTRA CORE MEM (API FastAPI, Postgres/pgvector, passerelle MCP, n8n, filebrowser).

## 1. Préparation du serveur
```bash
# Connexion SSH
ssh debian@<ip_vps>

# Mise à jour
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl ca-certificates git ufw htop
```

Activez le pare-feu UFW (ports 22, 80, 443, 8000, 5433, 5679, 8081, 8400 selon vos besoins).
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 5433/tcp
sudo ufw allow 5679/tcp
sudo ufw allow 8081/tcp
sudo ufw allow 8400/tcp
sudo ufw enable
```

## 2. Installation Docker & Compose
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker debian
# Relogin pour appliquer le groupe docker
```
Installez Docker Compose plugin :
```bash
sudo apt install docker-compose-plugin -y
```

## 3. Installation Postgres + pgvector (option native)
Pour utiliser l’image Compose (recommandé), passez directement à l’étape 4. Pour une installation native :
```bash
sudo apt install -y postgresql-16 postgresql-server-dev-16
sudo -u postgres psql -c "CREATE DATABASE sentra_core;"
sudo -u postgres psql -c "CREATE USER sentra WITH PASSWORD 'sentra';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sentra_core TO sentra;"
sudo -u postgres psql -d sentra_core -c "CREATE EXTENSION IF NOT EXISTS vector;"
```
Note : le docker-compose embarque déjà `ankane/pgvector:pg16` avec les mêmes identifiants.

## 4. Déploiement SENTRA CORE MEM
```bash
sudo mkdir -p /opt/sentra
sudo chown debian:debian /opt/sentra
cd /opt/sentra
git clone https://github.com/NexorAgent/SENTRA_CORE_MEM.git src
cd src
cp .env.example .env
```
Éditez `.env` :
- `DATABASE_URL=postgresql+psycopg://sentra:sentra@postgres:5432/sentra_core`
- `N8N_WEBHOOK_URL=https://n8n.example.com/webhook/...`
- `GOOGLE_CREDENTIALS_FILE=/vault/secrets/google_service_account.json`
- `EMBEDDING_MODEL_NAME` (optionnel)

Placez les secrets :
```bash
sudo mkdir -p /opt/sentra/secrets
sudo chown -R debian:debian /opt/sentra/secrets
# Copiez les credentials Google ici si nécessaire
```

## 5. Lancement Docker Compose
```bash
cd /opt/sentra/src
docker compose up -d --build
# (Optionnel) lancer le worker embeddings
# docker compose --profile workers up -d vector-worker
```
Vérifications :
- `docker compose ps`
- `docker compose logs api -f`
- API disponible sur `http://<ip>:8000/health`
- Postgres sur `localhost:5433`

## 6. Service systemd (option)
Créez `/etc/systemd/system/sentra.service` :
```ini
[Unit]
Description=SENTRA Core MEM
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/opt/sentra/src
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
Restart=on-failure
User=debian

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable sentra
sudo systemctl start sentra
```

## 7. Sauvegardes
- **Postgres** : `docker exec sentra_postgres pg_dump -U sentra sentra_core > /opt/sentra/backups/$(date +%F).sql`
- **Archives mémoire** : synchroniser `memory/library/archives/` vers un stockage externe (rclone, rsync sur Google Drive).
- Activez la rotation des logs (`logs/` monté sur le host) avec logrotate si nécessaire.

## 8. Monitoring & sécurité
- Activer `fail2ban` sur SSH.
- Configurer `promtail`/`loki` ou `filebeat` pour collecter les logs container.
- Surveiller `docker stats`, `htop`.
- Mettre à jour régulièrement : `git pull` + `docker compose up -d --build`.

## 9. Variables utiles (production)
| Variable | Recommandation |
|----------|----------------|
| `ENVIRONMENT=production` | Distinction prod / dev |
| `DATABASE_ECHO=false` | Pas de logs SQL en prod |
| `EMBEDDING_DEVICE=cpu` | Pour VPS sans GPU |
| `VECTOR_TOP_K`, `VECTOR_MIN_SCORE` | Ajuster la pertinence |
| `SENTRA_API_BASE=https://api.example.com` | Consommé par MCP |

## 10. Mise à jour applicative
```bash
cd /opt/sentra/src
git pull
python -m pip install -r requirements.txt  # si mode sans docker
# ou : docker compose pull && docker compose up -d --build
python -m pytest
```
Appliquez les migrations SQL si vous en introduisez (Alembic à venir). Pour l'instant, la création des tables est automatique au démarrage FastAPI.

## 11. Points de terminaison à surveiller
- `GET /health` – statut API
- `GET /mcp/healthz` – passerelle MCP
- `docker compose logs postgres` – readiness Postgres

## 12. Raccourcis utiles
```bash
# Shell Postgres
psql postgresql://sentra:sentra@localhost:5433/sentra_core

# Nettoyer les volumes docker (attention données !)
docker compose down -v

# Redémarrage complet
systemctl restart sentra
```

Bonne installation !
