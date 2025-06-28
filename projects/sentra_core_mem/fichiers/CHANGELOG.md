# Changelog – SENTRA_CORE_MEM

## [v0.1] – 2025-05-24
### Added
- Initialisation du noyau mémoire SENTRA_CORE
- Script de gestion mémoire (`memory_manager.py`)
- Fichier `sentra_memory.json` compressé (exemple glyphique)
- Prompts système (`sentra_core.prompt.txt`)
- Code de conduite IA (`SENTRA_OATH.md`)
- Règles de compression glyphique (`glyph_rules.txt`)
- README initial

## [v0.2] – 2025-05-25
### Added
- Orchestrator IA en module Python (`sentra/orchestrator.py`)  
- Gestion centralisée des logs dans `logs/execution_log.txt` (mode append)  
- Agent Notion pour archivage et lecture des logs Notion  
- Générateur de rapports Markdown automatisé (`markdown_generator.py`)  
- Classement automatique des rapports dans `reports/YYYY/MM/`  
- Scripts de workflow Git :
  - `sentra_cycle.bat` (push automatique sur `dev`)  
  - `merge_to_main.bat` (merge manuel `dev`→`main`)  
- Dossiers de structure :
  - `docs/` (SENTRA_OATH.md, glyph_rules.txt)  
  - `logs/` (execution_log.txt)  
  - `reports/` (rapports horodatés)  

### Changed
- Chemins relatifs corrigés pour toujours trouver `memory/` et `logs/`  
- Slug regex ajustée pour nom de rapport fiable  
- Configuration globale déplacée dans `sentra_config.py`  
- Nettoyage de scripts et `.bat` obsolètes  

### Fixed
- `execution_log.txt` n’était pas en mode append  
- Générateur Markdown produisait un fichier vide si exécuté hors racine  
- Merge script `merge_to_main.bat` pour synchronisation correcte  

