# SENTRA_CORE_MEM — Mémoire IA autonome 🧠

**SENTRA_CORE_MEM** est un noyau IA capable de compresser ses souvenirs, d'orchestrer plusieurs agents, de fonctionner hors SaaS et maintenant d'exploiter un cortex IA local (DeepSeek R1) connecté en API. Le projet reste entièrement open source et modulable.

---

## Objectif
- Mémoriser chaque interaction utile
- Résumer à trois niveaux (humain, hybride, glyphique)
- Mobiliser des agents dédiés (Markdown, Notion, Discord…)
- Optimiser l'usage des tokens et la mémoire centrale (vectorielle)
- Bénéficier d’une IA reasoning en local (DeepSeek R1/7B via Ollama)
- Orchestrer l’automatisation via n8n, fallback cloud/local

---

## Architecture actuelle (MAJ 2025-07-15)

- **VPS OVH** : orchestration, mémoire centrale (ChromaDB), API REST (FastAPI), agents et automatisations (n8n), backups, logs, traçabilité
- **PC local (DeepSeek R1/7B quantisé)** : reasoning, résumé, brainstorming, agents spécialisés (via Ollama/llama.cpp, API REST locale ou tunnel sécurisé)
- **Interopérabilité** : Tunnel Cloudflare/Reverse proxy, fallback automatique OpenAI → DeepSeek local, workflow modulaire

---

## Structure du projet
```text
sentra_core_mem/
├── memory/            # Mémoire compressée (.json)
├── scripts/           # Encodeurs, agents, automatisations
├── sentra/            # Noyau, orchestrateur, vector search
├── reports/           # Rapports générés
├── logs/              # Journaux d'exécution
├── docs/              # Documentation, changelog, plannings
├── docker-compose.yml # Orchestration API, n8n, Discord, etc.
└── projects/          # Multimémoire, journal, sandbox/prod
```

## Installation et configuration
Cloner le dépôt :

bash
Copier
Modifier
git clone https://github.com/sentra-core/sentra_core_mem.git
cd sentra_core_mem
Créer un environnement virtuel puis installer les dépendances :

bash
Copier
Modifier
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
Copier .env.example en .env et renseigner les clés :

ini
Copier
Modifier
OPENAI_API_KEY=sk-...
NOTION_TOKEN=secret_...
NOTION_DB_ID=abcd1234...
DISCORD_BOT_TOKEN=MTA...
Vérifier configs/config.json puis lancer le test rapide :

bash
Copier
Modifier
python scripts/sentra_check.py
Aucun fichier .env n'est fourni dans le dépôt ; chaque environnement garde ses clés privées.

Utilisation de l'API
Démarrer l'API FastAPI
Pour tester localement l'API (plugin ChatGPT), lancez :

bash
Copier
Modifier
uvicorn scripts.api_sentra:app --reload --port 5000

Endpoints principaux

POST /write_note – ajouter une note
GET /get_notes – lire toute la mémoire JSON
GET /read_note – rechercher dans la mémoire
GET /get_memorial – journal Markdown d'un projet
POST /write_file – créer ou modifier un fichier
GET /list_files – lister un dossier
POST /delete_file – supprimer un fichier
POST /move_file – déplacer un fichier
POST /archive_file – archiver un fichier
POST /reprise – résumer un canal Discord
GET /check_env – tester la clé API
GET /legal – consulter la notice légale


### Exemples `curl`
```bash
curl -X POST http://localhost:8000/write_note \
     -H "Content-Type: application/json" \
     -d '{"text":"Nouvelle note","project":"sentra_core"}'

curl http://localhost:8000/get_notes

# Rechercher dans la mémoire
curl "http://localhost:8000/read_note?term=project"

# Lire le journal Markdown du projet
curl "http://localhost:8000/get_memorial?project=sentra_core"

# Écrire un fichier
curl -X POST http://localhost:8000/write_file \
     -H "Content-Type: application/json" \
     -d '{"project": "sentra_core", "filename": "todo.md", "content": "- [ ] Tâche"}'
```
```bash
# Supprimer un fichier
curl -X POST http://localhost:8000/delete_file \
     -H "Content-Type: application/json" \
     -d '{"path": "/tmp/test.txt"}'

# Déplacer un fichier
curl -X POST http://localhost:8000/move_file \
     -H "Content-Type: application/json" \
     -d '{"src": "/tmp/a.txt", "dst": "/tmp/b.txt"}'

# Archiver un fichier
curl -X POST http://localhost:8000/archive_file \
     -H "Content-Type: application/json" \
     -d '{"path": "/tmp/a.log", "archive_dir": "/tmp/archive"}'
```
Chaque écriture déclenche automatiquement un `git commit` suivi d'un `git push`. Les notes sont sauvegardées dans `memory/sentra_memory.json` ainsi que dans `projects/<nom>/fichiers/Z_MEMORIAL.md`. Lorsqu’un champ `project` est fourni, elles sont aussi ajoutées dans `projects/<slug>/fichiers/memoire_<slug>.md`.

## 🔒 Obfuscation glyphique
L'option `--obfuscate` du script `run_auto_translator.py` attribue des glyphes aléatoires à chaque balise. Le mapping généré est écrit dans un fichier `<nom>_mapping.json` (ou chemin défini par `--map-out`). **Attention :** perdre ce fichier rend la décompression impossible. Conservez-le précieusement ou lancez le script sans obfuscation si la récupération prévaut.

Pour restaurer un texte :
```python
from scripts.glyph.glyph_generator import decompress_with_dict
import json
mapping = json.load(open("FICHIER_mapping.json", "r", encoding="utf-8"))
plain = decompress_with_dict(glyph_text, mapping)
```

## 🔄 Vue d'ensemble du workflow
Un cycle complet peut être exécuté manuellement ou via scheduler :
```
encode → load → sync → report
```
Le script `sentra/orchestrator.py` centralise ces étapes et gère la distribution vers les agents.

## 📖 Exemples d'utilisation
### Créer et interroger une mémoire
```bash
python scripts/zmem_encoder.py -i docs/mon_texte.txt -n DEMO/MEM
python scripts/compose_prompt.py DEMO/MEM
```
📖 Exemples d'utilisation avancée
Orchestration mémoire : vector search (ChromaDB), résumé markdown, fusion intelligente de notes

Brainstorming/code/veille par DeepSeek R1 via API Ollama (voir planning)

Automatisation n8n : backup, synchronisation, extraction, dashboard, surveillance
```

### Orchestrateur & agents
```bash
# Encodage via l'orchestrateur
python sentra/orchestrator.py encode --input docs/mon_texte.txt --name DEMO/MEM

# Synchronisation Notion + Discord
python sentra/orchestrator.py sync --target all

# Génération de rapport pour une date
python sentra/orchestrator.py report --date 2025-06-01
```
Les agents peuvent aussi être appelés directement :
```bash
python scripts/agent_markdown.py           # Rapport Markdown
python scripts/agent_notion.py             # Synchronisation Notion
python sentra/zarch.py --query "Alpha"     # Recherche dans la mémoire
```

### Autres scripts utiles
```bash
python scripts/archive.py       # Archiver le projet
python scripts/main.py          # Test global de l'installation
```
> **Aucun fichier .env n’est fourni dans le repo.**
> La clé reste privée sur chaque environnement.

Les scripts Python lisent automatiquement la clé avec :
```python
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
```

## Documentation complémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

En mode Render/cloud, le push git effectif nécessite un token/clé SSH configuré. Les endpoints sont sécurisés par obscurité (non publics) mais peuvent être protégés (bearer token, etc.).

### Docker Compose
Un fichier `docker-compose.yml` permet de lancer l'API FastAPI, le bot Discord, n8n et l'orchestrateur :
```bash
docker compose up -d
```

🧭 PHASE 0 – Audit & Préparation (Semaine 0)
🎯 Objectif :
Préparer le terrain côté VPS pour accueillir toute l’architecture SENTRA_CORE_MEM (API, Orchestrateur, n8n, etc.) de façon sécurisée, stable et documentée.

✅ 0.1 — Audit du VPS
🔍 Vérifier les ressources disponibles
Connecte-toi en SSH :

bash
Copier
Modifier
ssh debian@<IP_DU_VPS>
Et lance les commandes suivantes :

bash
Copier
Modifier
# CPU
lscpu

# RAM
free -h

# Stockage
df -h

# Réseau + nom machine
hostnamectl && ip a
📌 Objectif : confirmer que ton VPS a au moins 2 vCPU, 4 Go RAM et 20 Go de libre pour les besoins de base.

🔐 Vérification sécurité SSH
bash
Copier
Modifier
# Vérifie si fail2ban est installé
sudo systemctl status fail2ban

# Vérifie si UFW est actif
sudo ufw status verbose
🔧 Si nécessaire :

bash
Copier
Modifier
# Installer fail2ban
sudo apt install fail2ban -y

# Installer et activer UFW
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
🐳 0.2 — Installation Docker / Docker Compose / Git
bash
Copier
Modifier
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajout de l’utilisateur au groupe Docker
sudo usermod -aG docker $USER
newgrp docker

# Vérification Docker
docker --version

# Docker Compose plugin (Debian >= 11)
sudo apt install docker-compose-plugin -y
docker compose version

# Installation Git
sudo apt install git -y
git --version
📁 0.3 — Création du dossier projet "propre"
bash
Copier
Modifier
# Clonage du projet
git clone https://github.com/NexorAgent/SENTRA_CORE_MEM.git
cd SENTRA_CORE_MEM

# Création du .env
cp .env.example .env
nano .env  # (adapter les clés API, ports, etc.)
📄 0.4 — Rédaction documentation initiale
Crée un fichier README_PHASE0.md avec :

markdown
Copier
Modifier
# 📄 SENTRA_CORE_MEM — Phase 0 : Audit & Préparation

## 🔍 VPS
- CPU : 2vCPU
- RAM : 4 Go
- Disque libre : 25 Go
- Nom de machine : sentra-core
- OS : Debian 11

## 🔐 Sécurité
- SSH activé, port : 22
- Fail2ban actif
- UFW actif, règles :
  - allow ssh
  - allow 80, 443 (pour Nginx / tunnel)
- OVH Firewall externe : désactivé (si cloudflared)

## 🐳 Docker & Git
- Docker : ✅ installé
- Docker Compose : ✅ OK (v2)
- Git : ✅ installé

## 📁 Dossier projet
- Structure clonée depuis GitHub
- .env généré avec clés API

## ✅ Vérifications OK
- SSH : ✅
- Git : ✅
- Docker : ✅
- Ports API & n8n ouverts : ✅
✅ 0.5 — Vérification finale
bash
Copier
Modifier
# Tester que tout fonctionne
docker --version
docker compose version
git status
📦 Fichiers à ajouter au Git (si projet privé)
plaintext
Copier
Modifier
📁 SENTRA_CORE_MEM/
├── README_PHASE0.md
├── .env.example
├── .gitignore
Tu peux aussi pousser les premières infos d’audit dans ton repo Git :

bash
Copier
Modifier
git add README_PHASE0.md
git commit -m "Ajout audit phase 0"
git push origin main
⏱️ Durée estimée
Étape	Durée max
Audit SSH + CPU/RAM	10 min
Installation Docker/Git	20 min
Configuration UFW	10 min
Clonage + .env	10 min
Rédaction README audit	15 min

⏳ Total : 1h max si tout est prêt.

© 2025 — Projet open‑source modulable ✨

## Licence
Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.
