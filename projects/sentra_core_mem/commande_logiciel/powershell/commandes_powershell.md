## 💻 Commandes PowerShell utiles

### Naviguer dans les dossiers
```powershell
cd "C:\Users\julie\Documents"
```

### Lister les fichiers d’un dossier
```powershell
Get-ChildItem
```

### Afficher le contenu d’un fichier
```powershell
Get-Content .\mon_fichier.txt
```

### Télécharger un fichier depuis Internet
```powershell
Invoke-WebRequest -Uri "https://exemple.com/fichier.txt" -OutFile "C:\fichier.txt"
```

### Vérifier si un programme est installé
```powershell
Get-Command nom_du_programme
```

### Supprimer un fichier
```powershell
Remove-Item .\ancien_fichier.txt
```

### Calculer le hash d’un fichier
```powershell
Get-FileHash -Path "C:\chemin\vers\fichier.txt" -Algorithm SHA256
```