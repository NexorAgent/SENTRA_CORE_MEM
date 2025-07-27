## 🖥️ Commandes utiles – VPS (Linux, SSH)

### Connexion SSH
```bash
ssh -p 49152 debian@146.59.235.7
```

### Transfert de fichiers avec `scp`
```bash
scp -P 49152 fichier.txt debian@146.59.235.7:/home/debian/
```

### Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

### Vérifier l’espace disque
```bash
df -h
```

### Lister les processus actifs
```bash
top
```

### Supprimer un fichier ou dossier protégé
```bash
sudo rm -rf /chemin/du/fichier
```

### Modifier les droits
```bash
sudo chown -R debian:debian /chemin/du/dossier
```

### Vérifier si un port est ouvert
```bash
sudo ss -tuln | grep 49152
```
### Sauvegarde vps drive 
```bash 
rclone copy -v ~/SENTRA_CORE_MEM "drive vps backup:sentra_backup"
```

### Verifier dossier sur vps  
```bash 
ls -l ~/SENTRA_CORE_MEM/projects/sentra_core_mem
et affiner par dossier ls -l ~/SENTRA_CORE_MEM/projects/sentra_core_mem/A_LIRE_AGENT
                       ls -l ~/SENTRA_CORE_MEM/projects/sentra_core_mem/commande_logiciel

```

### Sauvegarde vps drive 
```bash 
rclone copy -v ~/SENTRA_CORE_MEM "drive vps backup:sentra_backup"
```

### Acces a SENTRA_CORE_MEM
```bash 
cd ~/SENTRA_CORE_MEM
```

### arborescence
```bash 
cd ~/SENTRA_CORE_MEM && tree -L 2
```