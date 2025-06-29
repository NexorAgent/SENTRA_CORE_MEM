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

 codex/réécrire-readme-avec-sections-fusionnées
## Installation et configuration

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/sentra-core/sentra_core_mem.git
   cd sentra_core_mem
   ```
2. Créer un environnement virtuel puis installer les dépendances :
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copier `\.env.example` en `.env` et renseigner les clés :
   ```ini
   OPENAI_API_KEY=sk-...
   NOTION_TOKEN=secret_...
   NOTION_DB_ID=abcd1234...
   DISCORD_BOT_TOKEN=MTA...
   ```
4. Vérifier `configs/config.json` puis lancer le test rapide :
   ```bash
   python scripts/sentra_check.py
   ```

*Aucun fichier `.env` n'est fourni dans le dépôt ; chaque environnement garde ses clés privées.*

## Utilisation de l'API
=======
### Démarrer l'API FastAPI
Pour tester localement l'API (plugin ChatGPT), lancez :

```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

## 📁 Structure
 main

Démarrer le serveur local :
```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

codex/réécrire-readme-avec-sections-fusionnées
### Endpoints principaux
- `POST /write_note` – ajouter une note
- `GET /get_notes` – lire toute la mémoire JSON
- `GET /read_note` – rechercher dans la mémoire
- `GET /get_memorial` – journal Markdown d'un projet
- `POST /write_file` – créer ou modifier un fichier

## 🌐 Endpoints API

Un serveur *FastAPI* (voir `scripts/api_sentra.py`) expose plusieurs routes pour interagir avec la mémoire :
- `POST /write_note` – ajoute une note textuelle dans la mémoire (paramètre `project` optionnel)
- `GET /get_notes` – lit le fichier JSON complet (lecture de note)
- `GET /read_note` – recherche des notes par mot-clé ou affiche les dernières
- `GET /get_memorial` – renvoie le journal Markdown du projet choisi
- `POST /write_file` – crée ou met à jour un fichier dans `projects/<projet>/fichiers/`
- `GET /list_files` – lister un dossier
main
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
 codex/réécrire-readme-avec-sections-fusionnées


# Rechercher dans la mémoire
curl "http://localhost:8000/read_note?term=project"

# Lire le journal Markdown du projet
curl "http://localhost:8000/get_memorial?project=sentra_core"

# Écrire un fichier dans le projet "sentra_core"
curl -X POST http://localhost:8000/write_file \
     -H "Content-Type: application/json" \
     -d '{"project": "sentra_core", "filename": "todo.md", "content": "- [ ] Tâche"}'

# Consulter la notice et la licence
curl http://localhost:8000/legal
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
Chaque écriture déclenche automatiquement un `git commit` suivi d’un `git push`,
assurant la persistance des modifications. Les notes sont sauvegardées dans
`memory/sentra_memory.json` ainsi que dans `projects/<nom>/fichiers/Z_MEMORIAL.md`.
Lorsqu’un champ `project` est fourni, elles sont aussi ajoutées dans
`projects/<slug>/fichiers/memoire_<slug>.md`.


## 🔒 Obfuscation glyphique

L'option `--obfuscate` du script `run_auto_translator.py` attribue des glyphes
aléatoires à chaque balise. Le mapping généré est écrit dans un fichier
`<nom>_mapping.json` (ou chemin défini par `--map-out`).

**Attention :** perdre ce fichier rend la décompression impossible. Conservez-le
précieusement ou lancez le script sans obfuscation si la récupération prévaut.

Pour restaurer un texte :

```python
from scripts.glyph.glyph_generator import decompress_with_dict
import json
mapping = json.load(open("FICHIER_mapping.json", "r", encoding="utf-8"))
plain = decompress_with_dict(glyph_text, mapping)
```

## 🔐 Configuration

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

Les scripts Python lisent automatiquement la clé avec :
```python
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
```

## Obfuscation des glyphes

L'outil `mem_block.py` dispose de l'option `--obfuscate` pour exporter un bloc
avec des glyphes réassignés aléatoirement. Le mapping généré est écrit dans un
fichier `.map.json` afin de pouvoir décompresser le texte plus tard. Cette
méthode complique simplement la lecture directe et ne constitue pas une
protection cryptographique : toute personne possédant ce mapping peut retrouver
le contenu original.

11/06/2025

# SENTRA_CORE_MEM — IA mémoire autonome pilotable

## Objectif
Fournir une brique mémoire compressée, évolutive et 100% pilotable par agent (GPT, Discord, Notion…) — compatible multi-clone, multi-agent, et compression glyphique.

## Fonctionnalités clés
- Écriture/lecture mémoire via API REST (FastAPI/Swagger)
- Gestion multi-projets (project = slug agent/clone)
- Compression glyphique (token et stockage réduits)
- Contrôle total par agent (création, modification, auto-organisation mémoire)
- Robustesse prod (erreur git tolérée, commit facultatif, mémoire toujours écrite)
- Prêt à l’intégration Discord, Notion, LinkedIn, Outlook…
- API facilement extensible (delete, move, orchestrateur…)

## Endpoints principaux

| Endpoint      | Méthode | Usage                              |
|---------------|---------|-----------------------------------|
| /write_note   | POST    | Ajouter une note mémoire           |
| /write_file   | POST    | Créer ou modifier un fichier      |
| /get_memorial | GET     | Lire le journal Markdown d’un projet |
| /get_notes    | GET     | Lire tout le JSON mémoire          |
| /read_note    | GET     | Recherche simple dans la mémoire   |
| /reprise      | POST    | Résumer un canal Discord            |
| /legal        | GET     | Consulter NOTICE et licence        |
| /check_env    | GET     | Vérifier la clé API (debug)        |

| Endpoint       | Méthode | Usage                            |
|----------------|---------|----------------------------------|
| /write_note    | POST    | Ajouter une note mémoire         |
| /write_file    | POST    | Créer/éditer un fichier mémoire  |
| /get_memorial  | GET     | Lire la mémoire (markdown)       |
| /get_notes     | GET     | Lire tout le JSON mémoire        |
| /legal         | GET     | Notice légale / licence          |
| (à venir…)     | POST    | delete/move/orchestrate…         |

## Exemples d’utilisation

**Écrire une note mémoire (curl, Swagger, ou GPT plugin)** :
```bash
curl -X POST https://sentra-core-mem.onrender.com/write_note \
  -H "Content-Type: application/json" \
  -d '{"text":"Nouvelle idée IA !","project":"ALPHA"}'

Contrôle mémoire par agent/GPT
Tout agent GPT ou humain peut piloter :

la création et l’organisation mémoire

l’édition ou l’archivage de tout fichier

la structuration “vivante” des projets (logs, reports, backup…)

🧠 “SENTRA_CORE_MEM n’est pas une simple brique mémoire : c’est une base de savoir auto-organisée, prête à accueillir toute IA évolutive.”

Arborescence de référence
/memory/                 — stockage compressé (JSON, glyphique…)
/projects/<slug>/fichiers/ — markdown, logs, rapports par projet/clone
/scripts/                — agents, modules API, outils
/docs/                   — documentation, guide utilisateur

## Tableau de bord des actions
Un fichier `logs/actions.log` conserve les actions effectuées.
Le script `scripts/actions_dashboard.py` produit un résumé Markdown dans `logs/actions_report.md`.

### Exécution manuelle
```bash
python -m scripts.actions_dashboard
```

### Planification
Exemple cron quotidien :
```bash
0 2 * * * cd /chemin/vers/SENTRA_CORE_MEM && python -m scripts.actions_dashboard
 main
```
Chaque écriture déclenche automatiquement un `git commit` suivi d'un `git push`. Les notes sont stockées dans `memory/sentra_memory.json` ainsi que dans `projects/<slug>/fichiers/`.
 codex/réécrire-readme-avec-sections-fusionnées
## Documentation complémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

© 2025 — Projet open‑source sous licence [MIT](LICENSE).


En mode Render/cloud, le push git effectif nécessite un token/clé SSH configuré.

Les endpoints sont sécurisés par obscurité (non publics) mais peuvent être protégés (bearer token, etc.).

Notice rapide
Voir NOTICE.md pour le détail des cycles, agents, extensions, FAQ.


---
 codex/ajouter-fichier-docker-compose-root

## 📑 Documentation supplémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

 codex/mettre-à-jour-readme.md
### Docker Compose
Un fichier `docker-compose.yml` permet de lancer l'API FastAPI, le bot Discord, n8n et l'orchestrateur :

```bash
docker compose up -d
```
© 2025 — Projet open‑source modulable ✨

## Licence
Ce projet est distribuée sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.
 228a3aa670cbfd79800f8695cad5281122fe07c4

 main

© 2025 — Projet open-source modulable ✨
 main
