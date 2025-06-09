# NOTICE.md – Manuel d’utilisation **SENTRA\_CORE\_MEM**

> **Version : v0.2 – 01 juin 2025**
> *Révision majeure : enrichissement complet du manuel (installation détaillée, cycles d’usage, FAQ).*
> **Mainteneur :** Laurent / SENTRA CORE

---

## 1. Vue d’ensemble

**SENTRA\_CORE\_MEM** est une IA personnelle autonome — fonctionnant hors‑SaaS — qui :

* **Capture** vos interactions dans une *mémoire compressée* (glyphique) pour des recherches ultra‑rapides.
* **Orchestre** des *agents spécialisés* (Markdown, Notion, Discord, etc.) via `orchestrator.py`.
* **Automatise** ses cycles (encode → load → sync → report) en local ou via GitHub Actions.
* **Reste évolutive et 100 % open‑source** : modules plug‑and‑play, coûts API réduits.

<p align="center"><img src="https://placehold.co/800x220?text=SENTRA_CORE_MEM+Architecture" alt="diagramme" /></p>

---

## 2. Installation express

### 2.1  Pré‑requis

| Outil                  | Version minimale | Test de présence               |
| ---------------------- | ---------------- | ------------------------------ |
| **Python**             | 3.10             | `python --version`             |
| **Git**                | 2.30             | `git --version`                |
| **Make** *(optionnel)* | —                | `make --version` (Linux/macOS) |

> **Astuce :** Sous Windows, installez [Git Bash](https://gitforwindows.org/) pour bénéficier des commandes Unix.

### 2.2  Clonage & installation

```bash
# 1) Récupérer le dépôt
$ git clone https://github.com/sentra-core/sentra_core_mem.git
$ cd sentra_core_mem

# 2) Créer un environnement virtuel (fortement recommandé)
$ python -m venv .venv && source .venv/bin/activate  # PowerShell : .venv\Scripts\Activate.ps1

# 3) Installer les dépendances
$ pip install -r requirements.txt
```

### 2.3  Configuration initiale

1. Copiez `.env.example` en `.env` puis renseignez vos clés :

   ```ini
   OPENAI_API_KEY=sk-…
   NOTION_TOKEN=secret_…
   NOTION_DB_ID=abcd1234…
   DISCORD_BOT_TOKEN=MTA…
   ```
2. Vérifiez/éditez `config.py` (chemins, paramètres glyphiques, etc.).

### 2.4  Vérification

```bash
$ python scripts/sentra_check.py   # Santé du système
```

---

## 3. Arborescence de référence

```text
sentra_core_mem/
├── memory/            # JSON compressé + index
├── scripts/           # Scripts utilitaires et agents
├── sentra/            # Noyau, orchestrateur & glyphique
├── reports/           # Rapports Markdown générés
├── logs/              # Journaux d’exécution
└── docs/              # Documentation (ce dossier)
```

### 3.1  Fichiers système clés

| Fichier              | Rôle                                      |
| -------------------- | ----------------------------------------- |
| `sentra_memory.json` | Stockage persistant (compression level 1) |
| `glyph_rules.txt`    | Règles glyphiques IA/Humain – v1          |
| `SENTRA_OATH.md`     | Engagements éthiques                      |
| `config.py`          | Paramètres globaux                        |

---

## 4. Variables d’environnement

| Variable            | Description                         | Exemple     |
| ------------------- | ----------------------------------- | ----------- |
| `OPENAI_API_KEY`    | Clé OpenAI (optionnelle)            | `sk-…`      |
| `NOTION_TOKEN`      | Jeton Notion pour `agent_notion.py` | `secret_…`  |
| `NOTION_DB_ID`      | ID de la base Notion mémoire        | `abcd1234…` |
| `DISCORD_BOT_TOKEN` | Token du bot Discord                | `MTA…`      |

> **Windows** : `setx OPENAI_API_KEY "sk-…"` • **macOS/Linux** : `export OPENAI_API_KEY="sk-…"`

---

## 5. Mise en route rapide

### 5.1  Cycle local complet

```bash
$ ./sentra_cycle.bat          # Windows
# ou
$ bash sentra_cycle.sh        # Linux/macOS
```

Ce script enchaîne :
1. **encode** – traduit les logs en glyphes et met à jour `glyph_dict.json`.
2. **load** – insère le résultat compressé dans `sentra_memory.json`.
3. **sync** – envoie la mémoire vers Notion et Discord.
4. **report** – crée `reports/YYYY/MM/YYYY-MM-DD_rapport.md`.
5. Push Git automatique sur la branche `dev`.

### 5.2  Exemples de commandes manuelles

| Action                      | Commande                                 |
| --------------------------- | ---------------------------------------- |
| Générer un rapport Markdown | `python scripts/agent_markdown.py`       |
| Synchroniser avec Notion    | `python scripts/agent_notion.py`         |
| Rechercher dans la mémoire  | `python sentra/zarch.py --query "Alpha"` |

---

## 6. Cycles automatisés

### 6.1  Scheduler GitHub Actions

* Workflow : `.github/workflows/sentra_cycle.yml`
* Déclenchement quotidien **03 h 00 UTC** (modifiable via `cron:`).

### 6.2  Scheduler local (option)

Dans `Windows Task Scheduler` ou `cron`, ajoutez :

```cron
0 6 * * * /path/to/sentra_core_mem/sentra_cycle.sh
```

---

## 7. Agents & Intent Dispatcher

| Mot‑clé slash/CLI | Agent cible         | Description brève                         |
| ----------------- | ------------------- | ----------------------------------------- |
| `report`          | `agent_markdown.py` | Génère un rapport + envoie sur Discord    |
| `sync`            | `agent_notion.py`   | Pousse la mémoire vers Notion             |
| `mémoire`         | `ZARCH`             | Recherche sémantique dans `sentra_memory` |

Le **dispatcher** (dans `orchestrator.py`) mappe automatiquement l’intention détectée à l’agent.

---

## 8. Compression glyphique

### 8.1  Niveau 1 – IA/Humain (actif)

* Règles d’abréviation, synonymes et hachage léger.
* Gain moyen : **×4** sur la taille brute.

### 8.2  Niveau 2 – IA/IA (en développement)

* Alphabet étendu (unicode privé) + dictionnaire adaptatif.
* Cible : **×10** de compression.

<<<<<< codex/document-création-de-glyph-sets-et-compression
### 8.3  Création de nouveaux sets de glyphes

* L’outil `glyph_watcher.py` scanne un dossier de logs et génère un glyphe pour
  chaque terme trouvé :

```bash
python scripts/glyph/glyph_watcher.py logs/
```

* Pour un mot isolé, la fonction `forge_glyph()` du module `GLYPH_FORGER.py`
  retourne le symbole associé :

```bash
python -c "from scripts.GLYPH_FORGER import forge_glyph; print(forge_glyph('exemple'))"
```

Les glyphes produits sont stockés dans `memory/glyph_dict.json`.

### 8.4  Partage du dictionnaire entre agents

Tous les modules glyphiques lisent le chemin depuis la variable d’environnement
`GLYPH_DICT_PATH` (par défaut `memory/glyph_dict.json`). Pour mutualiser un même
dictionnaire sur plusieurs machines :

```bash
export GLYPH_DICT_PATH=/chemin/partage/glyph_dict.json
```

### 8.5  Compression par lot

Le script `run_auto_translator.py` applique les glyphes puis compresse en `zlib`
et `base85`. Exemple :

```bash
python scripts/run_auto_translator.py -i "docs/resume sentra.zlib.txt"
```

Sur ce fichier d’essai, la taille passe de 11 995 octets à 4 992 octets (×2,4)
pour la version `.zlib`, puis à 6 379 octets pour le bloc `.zmem` (×1,9). Intégrez
cette commande dans un script `.bat` ou un `for` shell pour traiter un répertoire
complet.

### 8.6  Intégration dans un pipeline IA

* Prédécompressez ou compressez vos jeux de données avant de les envoyer à
  `orchestrator.py` ou à un modèle tiers afin de réduire le nombre de tokens
  échangés.
* Partager `GLYPH_DICT_PATH` permet aux agents de décoder tout `MEM.BLOCK` via
  `mem_block.decode_mem_block()`.
* `pipeline_traducteur.py` ou `run_auto_translator.py` peuvent être appelés
  directement dans vos jobs CI/CD pour maintenir une mémoire compressée homogène.
=======
### 8.3  Ajouter un jeu de glyphes

1. Créez un fichier JSON dans `memory/` (ex : `glyph_dict_custom.json`).
2. Définissez la variable `GLYPH_DICT_PATH` pour pointer vers ce fichier.
3. Les agents l’utiliseront automatiquement pour générer ou lire les glyphes.

### 8.4  Partage et sauvegarde du dictionnaire

* Versionnez `glyph_dict.json` via Git pour tracer l’historique.
* Effectuez une copie compressée (`gzip glyph_dict.json`) après chaque session.
* Un dictionnaire propre améliore le taux de compression global.

### 8.5  Obfuscation

La fonction `make_mem_block()` peut exclure la table de correspondance
(`include_mapping=False`). Le texte compressé reste alors lisible
uniquement par les agents possédant le dictionnaire.
>>>>>> main

---

## 9. Déploiement du bot Discord *(facultatif)*

1. **Créer** l’application sur [https://discord.com/developers](https://discord.com/developers).
2. Activer `bot` + `applications.commands`, copier le token.
3. Définir `DISCORD_BOT_TOKEN` dans `.env`.
4. Hébergement gratuit : Render.com ;

   * Ajouter un **Blueprint Deploy** → GitHub ;
   * `Procfile` : `worker: python scripts/discord_bot.py`.
5. Exécuter `/sync` & `/report` pour test in‑server.

---

## 10. Tests & Dépannage

```bash
# Exécuter la suite de tests
$ python -m pytest -q
```

* **Logs** : consulter `logs/execution_log.txt` (append‑only).
* **Mode verbose** : `DEBUG=1` dans l’environnement.
* **Erreur Discord 401** → vérifier le token bot.
* **Erreur OpenAI quota** → passer `GPT_MODE=local` pour désactiver l’API.

---

## 11. Contribution & Roadmap

Toutes les PR sont bienvenues ! Consultez :

* `CHANGELOG.md` – suivi de versions.
* `PLANNING_SENTRA_CORE_MEM.md` – feuilles de route.

**Prochaines priorités (Semaine N+1)** :

1. Finaliser `NOTICE.md` (ce fichier).
2. Mettre à jour `CHANGELOG.md`.
3. Déployer le bot Discord en live.
4. Prototyper `ZARCH`.
5. Enrichir les intents du dispatcher.

---

## 12. FAQ rapide

> **Q :** Pas de clé OpenAI, puis‑je utiliser le projet ?
> **R :** Oui. Mettez `GPT_MODE=local` pour n’utiliser que la compression/expansion locale.
>
> **Q :** Comment réinitialiser la mémoire ?
> **R :** Supprimez/renommez `sentra_memory.json` puis relancez le cycle.
>
> **Q :** Quelle licence couvre le projet ?
> **R :** MIT – usage privé ou académique encouragé.


---

### 📄 **NOTICE.md** 09/06/2025

```markdown
# NOTICE — Mode d’emploi SENTRA_CORE_MEM

## Utilisation côté agent (GPT, Discord…)

- **Ajouter une note mémoire** :
  “Ajoute à la mémoire du projet ALPHA : ‘Idée IA compressée à archiver’”
- **Créer/modifier un fichier** :
  “Crée un fichier ‘reports/2025/ALPHA.md’ et écris ‘Résumé du sprint’”
- **Organisation personnalisée** :
  “Déplace tous les logs de 2024 dans ‘archives/2024’”
- **Backup/récupération** :
  “Exporte la mémoire complète du projet ZENITH en markdown”
- **Fine tuning possible** :
  “Prépare une base d’exemples pour réentrainer le modèle GPT”

## Extension API à venir

- Suppression/suppression en masse de fichiers
- Orchestration multi-action (envoi JSON pour batch de modifications)
- Dashboard et audit des actions agents (logging centralisé)

## Rappel de philosophie

SENTRA_CORE_MEM permet de :
- centraliser la connaissance de chaque agent/clone GPT
- garantir la traçabilité de chaque action mémoire (logs, backups…)
- ouvrir la voie à une IA auto-structurante (full autonomie projet, logs, fine-tuning)

---

## FAQ (raccourci)

- **Que se passe-t-il si git/push échoue sur Render ?**  
  La mémoire est TOUJOURS écrite, le commit est juste loggé en warning.

- **Est-ce qu’un agent peut vraiment tout organiser ?**  
  OUI, via les endpoints API, tout GPT peut réagencer la mémoire à sa guise.

- **Que faut-il pour un contrôle total ?**  
  Ajouter les endpoints `/delete_file`, `/move_file` (cf. README), configurer le push git avec une clé/token si besoin.

---

## Licence

MIT License


---

© 2025 **SENTRA CORE** – Licence MIT
