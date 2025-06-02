# SENTRA_CORE_MEM — Mémoire IA/IA Activable 🧠🦋

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

## 🔐 Configuration

- La clé API `OPENAI_API_KEY` doit être définie en variable d’environnement.
- Le fichier `configs/config.json` définit le modèle, température, etc.



---

© 2025 — Projet open-source modulable ✨
