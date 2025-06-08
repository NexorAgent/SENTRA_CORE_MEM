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

## 📁 Structure

```
scripts/    → encodeurs, agents, utilitaires
configs/    → config OpenAI, Discord, Notion
memories/   → .zmem compressés + .src lisibles
docs/       → MANUEL, README, rapports Markdown
```

## 🌐 Endpoints API

Un serveur *FastAPI* (voir `scripts/api_sentra.py`) expose plusieurs routes pour interagir avec la mémoire :
- `POST /write_note` – ajoute une note textuelle dans la mémoire
- `GET /get_notes` – lit le fichier JSON complet (lecture de note)
- `GET /get_memorial` – renvoie le journal Markdown du projet
- `POST /write_file` – crée ou met à jour un fichier dans `projects/<projet>/fichiers/`
- `POST /reprise` – résume un canal Discord
- `GET /check_env` – vérifie la clé API (debug)

### Exemples `curl`

```bash
# Écrire une note
curl -X POST http://localhost:8000/write_note \
     -H "Content-Type: application/json" \
     -d '{"text": "Nouvelle note"}'

# Lire la mémoire JSON
curl http://localhost:8000/get_notes

# Écrire un fichier dans le projet "sentra_core"
curl -X POST http://localhost:8000/write_file \
     -H "Content-Type: application/json" \
     -d '{"project": "sentra_core", "filename": "todo.md", "content": "- [ ] Tâche"}'
```

Chaque écriture déclenche automatiquement un `git commit` suivi d’un `git push`,
assurant la persistance des modifications. Les notes sont sauvegardées dans
`memory/sentra_memory.json` ainsi que dans `projects/<nom>/fichiers/Z_MEMORIAL.md`.


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

---

© 2025 — Projet open-source modulable ✨
