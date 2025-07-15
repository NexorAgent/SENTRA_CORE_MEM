# MANUEL D’UTILISATION — SENTRA_CORE_MEM v0.3

Créer, stocker, recharger et interroger des mémoires IA compressées `.zmem`.

---

## 📦 STRUCTURE DU PROJET

```
SENTRA_CORE_MEM/
├── scripts/          → Scripts Python principaux (.py)
├── configs/          → Fichiers de config : OpenAI, Discord, Notion
├── launchers/        → Fichiers .bat (lanceurs Windows)
├── memories/         → Mémoires compressées (.zmem, .src)
├── docs/             → Rapports, README, MANUEL
```

---

## 🔧 CONFIGURATION

1. **Clé OpenAI API**  
   Ajouter dans les variables d’environnement Windows :
   - Nom : `OPENAI_API_KEY`
   - Valeur : `sk-...`

2. **Fichier `config.json`**
   Situé dans `configs/config.json`, il contient :
   ```json
   {
     "model": "gpt-4",
     "temperature": 0.5,
     "max_tokens": 2048
   }
   ```

---

## 📥 CRÉER UNE MÉMOIRE `.zmem`

### ▶️ Commande :
```bash
python scripts/zmem_encoder.py -i docs/mon_texte.txt -n NOM/MEM
```

### 📄 Résultat :
- `memories/NOM/MEM.zmem` (compressé)
- `memories/NOM/MEM.zmem.src` (lisible)
- Mise à jour de `configs/memory_index.json`

---

## 🔁 INTERROGER LA MÉMOIRE AVEC GPT

```bash
python scripts/compose_prompt.py NOM/MEM
```

- Charge la mémoire
- Envoie un prompt automatique à OpenAI (via `OPENAI_API_KEY`)
- Affiche la réponse

---

## 🧠 SIMULER UN AGENT IA

```bash
python scripts/main_agents.py
```

Utilise :
- `configs/config.json`
- `configs/discord_config.py` ou `notion_config.py` si activés

---

## 📝 GÉNÉRER UN RAPPORT MARKDOWN

```bash
python scripts/markdown_generator.py
```

Génère :
- `docs/memoire_generee.md` à partir de la dernière mémoire `.src`

---

## 🗃️ ARCHIVER LE PROJET (sans .git, logs…)

```bash
python scripts/archive.py
```

Produit un dossier daté dans `archive/`.

---

## 🔄 TEST GLOBAL DE L’INSTALLATION

```bash
python scripts/main.py
```

Vérifie que GPT répond bien à une requête simple.

---

## 🆘 SUPPORT

📩 Contact : Frédéric Tabary  
🔗 LinkedIn : [https://www.linkedin.com/in/frederictabary](https://www.linkedin.com/in/frederictabary)  
📞 Téléphone : 06 45 60 50 23

---

© 2025 — SENTRA_CORE_MEM🦋 par ZORAN IA
