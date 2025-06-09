# SENTRA_CORE_MEM — Mémoire IA/IA Activable 🧠

**SENTRA_CORE_MEM** est un noyau IA autonome capable de compresser ses souvenirs, d'orchestrer plusieurs agents spécialisés et de fonctionner hors‑SaaS. Le projet reste 100 % open‑source et modulable.

## 🔍 Objectif
- Mémoriser automatiquement chaque interaction utile
- Résumer en 3 niveaux (humain / hybride / glyphique)
- Appeler des agents dédiés (Markdown, Notion, Discord…)
- Agir avec rigueur et économie de tokens

## 📂 Structure projet
```
sentra_core_mem/
├── memory/            # Mémoire compressée (.json)
├── scripts/           # Encodeurs, agents, utilitaires
├── sentra/            # Noyau, orchestrateur & recherche
├── reports/           # Rapports générés
├── logs/              # Journaux d'exécution
└── docs/              # Documentation (manuel, changelog…)
```

## 🚀 Installation

### Pré‑requis
| Outil | Version minimale | Vérification |
| ----- | ---------------- | ------------ |
| **Python** | 3.10 | `python --version` |
| **Git** | 2.30 | `git --version` |
| **Make** *(optionnel)* | — | `make --version` |

### Clonage & dépendances
```bash
# Récupérer le dépôt
$ git clone https://github.com/sentra-core/sentra_core_mem.git
$ cd sentra_core_mem

# Environnement virtuel (conseillé)
$ python -m venv .venv && source .venv/bin/activate

# Installer les packages
$ pip install -r requirements.txt
```

<<<<<<< HEAD
### Démarrer l'API FastAPI
Pour tester localement l'API (plugin ChatGPT), lancez :

```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

## 📁 Structure
=======
### Configuration initiale
1. Copier `.env.example` en `.env` puis renseigner :
   ```ini
   OPENAI_API_KEY=sk-...
   NOTION_TOKEN=secret_...
   NOTION_DB_ID=abcd1234...
   DISCORD_BOT_TOKEN=MTA...
   ```
2. Vérifier `configs/config.json` (modèle, température…).
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4

### Vérification
```bash
$ python scripts/sentra_check.py
```

<<<<<<< HEAD
## 🌐 Endpoints API

Un serveur *FastAPI* (voir `scripts/api_sentra.py`) expose plusieurs routes pour interagir avec la mémoire :
- `POST /write_note` – ajoute une note textuelle dans la mémoire (paramètre `project` optionnel)
- `GET /get_notes` – lit le fichier JSON complet (lecture de note)
- `GET /read_note` – recherche des notes par mot-clé ou affiche les dernières
- `GET /get_memorial` – renvoie le journal Markdown du projet choisi
- `POST /write_file` – crée ou met à jour un fichier dans `projects/<projet>/fichiers/`
- `POST /reprise` – résume un canal Discord
- `GET /check_env` – vérifie la clé API (debug)

### Exemples `curl`

```bash
# Écrire une note dans le projet "sentra_core"
curl -X POST http://localhost:8000/write_note \
     -H "Content-Type: application/json" \
     -d '{"text": "Nouvelle note", "project": "sentra_core"}'

# Lire la mémoire JSON
curl http://localhost:8000/get_notes

# Rechercher dans la mémoire
curl "http://localhost:8000/read_note?term=project"

# Lire le journal Markdown du projet
curl "http://localhost:8000/get_memorial?project=sentra_core"

# Écrire un fichier dans le projet "sentra_core"
curl -X POST http://localhost:8000/write_file \
     -H "Content-Type: application/json" \
     -d '{"project": "sentra_core", "filename": "todo.md", "content": "- [ ] Tâche"}'
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
=======
## 🔄 Vue d'ensemble du workflow
Un cycle complet peut être exécuté manuellement ou via scheduler :
```
encode → load → sync → report
```
Le script `sentra/orchestrator.py` centralise ces étapes et gère la distribution vers les agents.
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4

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

<<<<<<< HEAD
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

09/06/2025

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

| Endpoint       | Méthode | Usage                            |
|----------------|---------|----------------------------------|
| /write_note    | POST    | Ajouter une note mémoire         |
| /write_file    | POST    | Créer/éditer un fichier mémoire  |
| /get_memorial  | GET     | Lire la mémoire (markdown)       |
| /get_notes     | GET     | Lire tout le JSON mémoire        |
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

Sécurité et bonnes pratiques
Les agents sont puissants : active le log ou le versionning git pour tout changement critique.

En mode Render/cloud, le push git effectif nécessite un token/clé SSH configuré.

Les endpoints sont sécurisés par obscurité (non publics) mais peuvent être protégés (bearer token, etc.).

Notice rapide
Voir NOTICE.md pour le détail des cycles, agents, extensions, FAQ.


---
=======
## 📑 Documentation supplémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

 codex/mettre-à-jour-readme.md
© 2025 — Projet open‑source modulable ✨

## Licence
Ce projet est distribuée sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4

© 2025 — Projet open-source modulable ✨
 dev
