## 📁 Bonne conduite de création de fichiers SENTRA_CORE_MEM

🗓️ *Mise à jour : 2025-07-15*

---

### 🔐 Droit & permissions
- ❌ Ne pas créer de fichier ou dossier avec les droits `root` (sauf nécessité documentée)
- ✅ Toujours créer/modifier en tant qu'utilisateur `debian`

### 📂 Structure & nommage
- ⚠️ Ne pas créer de dossier intermédiaire comme `fichiers/...` si la structure attendue est directe
- 📁 Toujours nommer les dossiers de façon explicite et cohérente avec l’usage (ex. `commande_logiciel/vps` ✅)
- ❌ Ne pas recréer un dossier déjà existant (ex : `sentra_core_mem` vs `sentra_core_memoire`)
- ✅ Fusionner si redondance, supprimer les doublons après confirmation
- 🛑 Ne crée de nouveaux dossiers **que sur demande explicite**

### 📜 Documentation
- Chaque ajout important (script, protocole, mémoire) doit être documenté dans `A_LIRE_AGENT` ou `docs/`
- Toujours expliquer dans les commits ou messages la raison d’un ajout de fichier ou modification

### 📂 Synchronisation & accès
- WinSCP ou toute interface de synchro doit être surveillée → tester visibilité et permissions
- Vérifier que le fichier apparaît bien dans le VPS et en local après modification

---

🧠 Ce fichier est relu automatiquement au démarrage si présent dans `A_LIRE_AGENT`
📌 Pour forcer sa relecture : « Relis les consignes A_LIRE_AGENT »