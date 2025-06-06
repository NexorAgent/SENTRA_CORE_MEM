# SENTRA_CORE_MEM — Mémoire IA/IA Activable 🧠🦋

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

### Configuration initiale
1. Copier `.env.example` en `.env` puis renseigner :
   ```ini
   OPENAI_API_KEY=sk-...
   NOTION_TOKEN=secret_...
   NOTION_DB_ID=abcd1234...
   DISCORD_BOT_TOKEN=MTA...
   ```
2. Vérifier `configs/config.json` (modèle, température…).

### Vérification
```bash
$ python scripts/sentra_check.py
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

## 📑 Documentation supplémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

 codex/mettre-à-jour-readme.md
© 2025 — Projet open‑source modulable ✨

## Licence
Ce projet est distribuée sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

© 2025 — Projet open-source modulable ✨
 dev
