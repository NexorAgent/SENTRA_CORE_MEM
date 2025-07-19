## 🔐 Sécurité SENTRA_CORE_MEM – Journal 2025

### 📅 Date : 13–14 juillet 2025

Ce fichier fusionne :
- Journal sécurité Z_JOURNAL_SECURITE_2025.md (supprimé)
- Analyse FIREWALL_OVH_VS_VPS.md (supprimé)

---

## 1. 🔧 Blocage réseau initial et diagnostic

**Symptôme** : les services API, Discord, Notion, et n8n en Docker étaient inaccessibles depuis l'extérieur.

**Cause principale** : OVH active automatiquement son "Edge Firewall" en cas de détection de comportements suspects, bloquant DNS (UDP/53) et connexions entrantes.

**Diagnostic confirmé** par :
- DNS Google (8.8.8.8), Cloudflare (1.1.1.1), Quad9 (9.9.9.9) inaccessibles
- DNS OVH (213.186.33.99) partiellement fonctionnel

### ✅ Correctifs appliqués :
- Configuration de `/etc/resolv.conf` avec `nameserver 213.186.33.99`
- Désactivation manuelle du pare-feu OVH via l’espace client OVH
- Réactivation des tunnels Cloudflare → fonctionnement immédiat de tous les services

---

## 2. 🐳 Remise en route de la stack Docker

- Réparation des chemins dans `docker-compose.yml`
- Ajout du bloc `dns:` dans chaque service Docker
- Vérification DNS interne avec `nslookup` dans les conteneurs
- Redémarrage des services : `api`, `discord`, `orchestrator`, `n8n`

---

## 3. 🔐 Firewall local VPS (remplaçant UFW)

### Installation & configuration :
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 49152/tcp   # SSH
sudo ufw allow 443,80/tcp  # HTTP/HTTPS
sudo ufw allow 5678/tcp    # n8n
sudo ufw allow 7844/tcp    # Cloudflared
sudo ufw allow 8000/tcp    # API
sudo ufw enable
```

- Résultat : toutes les connexions nécessaires sont autorisées
- Aucun blocage depuis ou vers les services

---

## 4. 📌 Recommandations & précautions

- Ne jamais **activer le firewall OVH** en usage SENTRA → il prend le dessus même désactivé localement
- Utiliser uniquement `ufw` ou `iptables` sur le VPS
- Toujours tester la résolution DNS avec : `dig`, `nslookup`, etc.
- Documenter toutes les IPs, ports, services ouverts
- Stocker `cloudflared` comme service permanent (systemd)

---

## ✅ Statut final

- Stack SENTRA_CORE_MEM **100% opérationnelle**
- Services sécurisés via UFW, accès externes validés
- Sauvegarde journalière rclone vers Google Drive mise en place
- Rapport automatisé généré le 14 juillet 2025