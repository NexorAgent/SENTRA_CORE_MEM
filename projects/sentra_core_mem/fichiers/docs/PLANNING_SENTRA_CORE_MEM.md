## [2025-07-20] Mise à jour planning : avancée SENTRA_CORRECTOR++ v1.0

### ✅ Tâches réalisées
- Suppression Gemini & Node, nettoyage legacy
- Intégration agent OpenRouter (deepcoder-14b-preview, .env)
- Endpoint `/correct_file` opérationnel (FastAPI)
- Tests réels sur pipeline de correction automatique

### 🔜 À faire
- Endpoint `/correct_folder` pour batch multi-fichiers
- Sélecteur dynamique du modèle IA (API/.env)
- Reporting vers Notion, Discord, GitHub
- Extension architecture multi-agent (summarizer, vectorizer, Codex)
- Fallback IA automatique

### ⚙️ Rappels techniques
- Prompts IA : scripts/prompts/openrouter_prompts.yaml
- Agent principal : agent_openrouter.py
- Entrée API : /correct_file
