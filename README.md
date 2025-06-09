# SENTRA_CORE_MEM — Mémoire IA/IA Activable 🧠

# SENTRA_CORE_MEM

🧠 **SENTRA_CORE_MEM** est un noyau IA autonome, conçu pour centraliser mémoire, réflexion critique, compression glyphique et pilotage d’agents.

## 🔍 Objectif
Construire une intelligence artificielle modulaire et mémorielle capable de :
- mémoriser automatiquement chaque interaction utile
- résumer en 3 niveaux (humain / hybride / glyphique)
- appeler des agents spécialisés (Forge, Réseau, Analyse…)
- agir avec rigueur, cohérence, sourcing et économie de tokens

## 📂 Structure projet

sentra_core_mem/
├── memory/ # Mémoire compressée (.json)
├── prompts/ # Prompts systèmes (ex : sentra_core.prompt.txt)
├── scripts/ # Fonctions Python appelées par main
├── SENTRA_OATH.md # Serment comportemental IA
├── glyph_rules.txt # Normes de compression glyphique (N3)
├── main.py # Point d'entrée local
├── .env # Clé API OpenAI
└── requirements.txt # Dépendances


## 🧠 Fonctionnement
1. Chargement du prompt + mémoire (5 dernières entrées)
2. Réponse GPT-4 avec :
   - Résumé utilisateur
   - Résumé glyphique
   - Sauvegarde auto dans `sentra_memory.json`
3. Rappel mémoire sur demande (“résume tout ce qui concerne le projet mémoire”)

## 🛠️ Modules en développement
- [x] Mémoire locale automatique
- [ ] Mémoire Notion (niveau 2)
- [ ] Appels vocaux via Discord
- [ ] Routage d'agents par spécialité (SENTRA.FORGE, SENTRA.POST...)

---

# 🔧 UTILISATION TECHNIQUE (DOCS)

Système modulaire pour création, compression et interrogation de **mémoires IA/IA**.  
Utilise OpenAI GPT pour encoder, recharger et interagir avec des blocs de mémoire compressée `.zmem`.

## ⚙️ Fonctionnalités principales

- 🧠 Encodage mémoire IA sous format `.zmem` avec dictionnaire symbolique
- 🔁 Rechargement et interrogation par GPT (mode système)
- 📤 Export Markdown des mémoires
- 🧩 Compatible Discord et Notion via agents
- 🔒 Séparation configuration/API dans `/configs/`

## 🚀 Utilisation rapide

```bash
python scripts/zmem_encoder.py -i docs/mon_texte.txt -n TEST/MEM
python scripts/compose_prompt.py TEST/MEM
```

### Démarrer l'API FastAPI
Pour tester localement l'API (plugin ChatGPT), lancez :

```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

## 📁 Structure

```
scripts/    → encodeurs, agents, utilitaires
configs/    → config OpenAI, Discord, Notion
memories/   → .zmem compressés + .src lisibles
docs/       → MANUEL, README, rapports Markdown
```

## 🌐 Endpoints API

Un serveur *FastAPI* (voir `scripts/api_sentra.py`) expose plusieurs routes pour interagir avec la mémoire :
- `POST /write_note` – ajoute une note textuelle dans la mémoire (paramètre `project` optionnel)
- `GET /get_notes` – lit le fichier JSON complet (lecture de note)
- `GET /read_note` – recherche des notes par mot-clé ou affiche les dernières
- `GET /get_memorial` – renvoie le journal Markdown du projet choisi
- `POST /write_file` – crée ou met à jour un fichier dans `projects/<projet>/fichiers/`
- `POST /reprise` – résume un canal Discord
- `GET /check_env` – vérifie la clé API (debug)
- `GET /legal` – affiche la notice légale ou la licence du projet

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

- La clé API `OPENAI_API_KEY` doit être définie en variable d’environnement.
- Le fichier `configs/config.json` définit le modèle, température, etc.

- ## Sécurité des clés API

La clé OpenAI (et toute clé sensible) ne doit jamais être committée dans le code ni dans les fichiers de configuration.  
Elle doit être fournie comme **variable d’environnement** :

- **Sur Windows** :
  - Ouvrir PowerShell ou Git Bash
  - Exécuter :  
    `setx OPENAI_API_KEY "ta-clé-ici"`
  - (Redémarrer le terminal pour prise en compte)

- **Sur Render.com / autre hébergeur** :
  - Ajouter la variable dans les paramètres “Environment Variables” du projet (OPENAI_API_KEY)

- **Sur GitHub Actions** :
  - Définir la clé comme “Repository Secret” (Settings > Secrets and variables > Actions > New repository secret)

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
```
(ou adapter un workflow GitHub Actions sur le modèle de `.github/workflows/zsync.yml`).


Sécurité et bonnes pratiques
Les agents sont puissants : active le log ou le versionning git pour tout changement critique.

En mode Render/cloud, le push git effectif nécessite un token/clé SSH configuré.

Les endpoints sont sécurisés par obscurité (non publics) mais peuvent être protégés (bearer token, etc.).

Notice rapide
Voir NOTICE.md pour le détail des cycles, agents, extensions, FAQ.


---

© 2025 — Projet open-source modulable ✨
