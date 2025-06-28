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

Démarrer le serveur local :
```bash
uvicorn scripts.api_sentra:app --reload --port 5000
```

### Endpoints principaux
- `POST /write_note` – ajouter une note
- `GET /get_notes` – lire toute la mémoire JSON
- `GET /read_note` – rechercher dans la mémoire
- `GET /get_memorial` – journal Markdown d'un projet
- `POST /write_file` – créer ou modifier un fichier
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
```
Chaque écriture déclenche automatiquement un `git commit` suivi d'un `git push`. Les notes sont stockées dans `memory/sentra_memory.json` ainsi que dans `projects/<slug>/fichiers/`.

## Documentation complémentaire
- [CHANGELOG](docs/CHANGELOG.md)
- [PLANNING](docs/PLANNING_SENTRA_CORE_MEM.md)

© 2025 — Projet open‑source sous licence [MIT](LICENSE).
