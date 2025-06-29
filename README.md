# SENTRA_CORE_MEM — Mémoire IA autonome 🧠

**SENTRA_CORE_MEM** est un noyau IA capable de compresser ses souvenirs, d'orchestrer plusieurs agents et de fonctionner hors SaaS. Le projet reste entièrement open source et modulable.

## Objectif
- Mémoriser chaque interaction utile
- Résumer à trois niveaux (humain, hybride, glyphique)
- Mobiliser des agents dédiés (Markdown, Notion, Discord…)
- Optimiser l'usage des tokens

## Structure du projet
```text
sentra_core_mem/
├── memory/            # Mémoire compressée (.json)
├── scripts/           # Encodeurs, agents et utilitaires
├── sentra/            # Noyau, orchestrateur et recherche
├── reports/           # Rapports générés
├── logs/              # Journaux d'exécution
└── docs/              # Documentation
```

## Installation et configuration
1. Cloner le dépôt :
```bash
git clone https://github.com/sentra-core/sentra_core_mem.git
cd sentra_core_mem
```
2. Créer un environnement virtuel puis installer les dépendances :
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
3. Copier `.env.example` en `.env` et renseigner les clés :
```ini
OPENAI_API_KEY=sk-...
NOTION_TOKEN=secret_...
NOTION_DB_ID=abcd1234...
DISCORD_BOT_TOKEN=MTA...
```
4. Vérifier `configs/config.json` puis lancer le test rapide :
```bash
python scripts/sentra_check.py
```
*Aucun fichier `.env` n'est fourni dans le dépôt ; chaque environnement garde ses clés privées.*

## Utilisation de l'API

### Démarrer l'API FastAPI
Pour tester localement l'API (plugin ChatGPT), lancez :
```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

### Endpoints principaux
- `POST /write_note` – ajouter une note
- `GET /get_notes` – lire toute la mémoire JSON
- `GET /read_note` – rechercher dans la mémoire
- `GET /get_memorial` – journal Markdown d'un projet
- `POST /write_file` – créer ou modifier un fichier
- `GET /list_files` – lister un dossier
- `POST /delete_file` – supprimer un fichier
- `POST /move_file` – déplacer un fichier
- `POST /archive_file` – archiver un fichier
- `POST /reprise` – résumer un canal Discord
- `GET /check_env` – tester la clé API
- `GET /legal` – consulter la notice légale

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

© 2025 — Projet open‑source modulable ✨

## Licence
Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.
