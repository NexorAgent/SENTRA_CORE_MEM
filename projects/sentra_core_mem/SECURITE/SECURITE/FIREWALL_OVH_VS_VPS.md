## 🔐 Firewall OVH vs Firewall VPS — SENTRA_CORE_MEM

### 📅 Mise à jour : 14 juillet 2025

---

### 🧠 Constat
Lors de la remise en service du projet SENTRA_CORE_MEM sur un VPS OVH, nous avons constaté des blocages répétés sur les services utilisant :
- DNS externes (Google, Cloudflare, Quad9...)
- Tunnels Cloudflare
- Intégrations Discord et Notion via API

---

### 🔍 Analyse
Le **firewall réseau OVH** (aussi appelé Edge Firewall) agit **avant** l'accès au VPS et filtre certaines connexions **entrantes ET sortantes**. Il a notamment :
- Bloqué le **port UDP 53** (résolution DNS)
- Empêché la création du tunnel Cloudflare
- Rendu inopérants les appels Discord ou Notion depuis Docker

En cas d'attaque détectée par OVH (DDoS par exemple), ce firewall peut être **activé automatiquement**, **même s’il a été désactivé manuellement**.

---

### 🛠️ Correctifs appliqués
- 🔁 **Désactivation manuelle du firewall OVH** dans l’espace client
- 🔐 **Remplacement du firewall par un `ufw` local** sur le VPS :
  ```bash
  sudo apt install ufw
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow 22,80,443,8000,5678/tcp
  sudo ufw enable
  ```
- 📌 Résolution DNS confiée au DNS OVH :
  ```bash
  echo "nameserver 213.186.33.99" | sudo tee /etc/resolv.conf
  ```
- ✅ Tunnel Cloudflare relancé sans problème

---

### ✅ Résultat
- Accès stable et sécurisé via UFW local
- Tous les services (Cloudflare, API, Discord, Notion) **fonctionnels**
- Documenté pour toute future réinitialisation ou montée en prod

---

### 📌 À retenir
| Élément            | Type       | Localisation | Rôle principal                  |
|--------------------|------------|---------------|----------------------------------|
| Firewall OVH       | Edge       | Réseau OVH    | Défense contre attaques DDoS    |
| Firewall VPS (UFW) | Applicatif | VPS local     | Gestion fine du trafic autorisé |