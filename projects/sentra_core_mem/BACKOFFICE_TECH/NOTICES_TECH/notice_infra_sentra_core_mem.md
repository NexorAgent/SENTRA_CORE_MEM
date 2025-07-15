# Notice de fonctionnement — **Infrastructure SENTRA_CORE_MEM**

> **Public cible :** DevOps/SRE confirmé·e · **Version :** 1.0 · **MAJ :** 2025‑07‑10
>
> Cette notice décrit la pile réseau déployée sur le VPS (OVH, Debian 12) et son intégration Cloudflare Tunnel pour exposer les services **n8n** et **API mémoire** de manière sécurisée.

---

## 1. Topologie globale

```mermaid
flowchart TD
    subgraph VPS (OVH : 2 vCPU / 2 Go)
        direction TB
        A[Sentra API\nPort 8000]--Docker bridge-->NW
        B[n8n\nPort 5678]--Docker bridge-->NW
        C[cloudflared\nTunnel daemon]--QUIC-->CF((Cloudflare Edge))
        style C fill:#ffd9b3,stroke:#ff9900,stroke-width:2px
    end
    CF--CNAME proxied-->User[(Navigateurs / Discord bot)]
```

* **NW** : réseau Docker `sentra_network` (bridge) `172.19.0.0/16`.
* **cloudflared** établit 4 connexions QUIC/TLS sortantes → **Cloudflare Edge**.
* Aucun port entrant n’est ouvert sur le VPS ; seul le port 22 (SSH) reste filtré par OVH FW.

---

## 2. DNS & Tunnel Cloudflare

| Hostname                | Type      | Valeur                                                  | Proxy     | Origine ciblée           |
| ----------------------- | --------- | ------------------------------------------------------- | --------- | ------------------------ |
| `api.sentracoremem.ovh` | **CNAME** | `3d984c85-6c40-4164-9841-c8c5022110ed.cfargotunnel.com` | ☁️ Orange | `http://sentra_api:8000` |
| `n8n.sentracoremem.ovh` | **CNAME** | `3d984c85-6c40-4164-9841-c8c5022110ed.cfargotunnel.com` | ☁️ Orange | `http://sentra_n8n:5678` |

> * Tunnel ID : **`3d984c85‑6c40‑4164‑9841‑c8c5022110ed`**
> * Credentials : `/etc/cloudflared/3d984c85‑6c40‑4164‑9841‑c8c5022110ed.json`

### 2.1 Fichier `cloudflared/config.yml`

```yaml
tunnel: 3d984c85-6c40-4164-9841-c8c5022110ed
credentials-file: /etc/cloudflared/3d984c85-6c40-4164-9841-c8c5022110ed.json

ingress:
  - hostname: api.sentracoremem.ovh
    service: http://sentra_api:8000
  - hostname: n8n.sentracoremem.ovh
    service: http://sentra_n8n:5678
  - service: http_status:404  # fallback safety
```

* **Propagation DNS** typique : < 60 s (Cloudflare autoritaire).
* Santé tunnel : visible dans Zero Trust ► *Networks › Tunnels* → doit être **SAIN**.

---

## 3. Stack Docker

```yaml
# Extrait clé docker‑compose.yml
services:
  sentra_api:
    build: .
    ports: ["8000:8000"]
    networks: [sentra_network]
  sentra_n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
    networks: [sentra_network]
  sentra_discord:
    build:
      context: .
      dockerfile: Dockerfile.discord
    networks: [sentra_network]
  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel run sentra-core-mem
    volumes:
      - ./cloudflared:/etc/cloudflared
    networks: [sentra_network]
networks:
  sentra_network:
    driver: bridge
```

### Points durs

* **Pas de `network_mode: host`** (inutile ; rester en bridge).
* `cloudflared` lit le YAML + credentials montés en volume **lecture seule**.
* Redémarrage orchestré : `docker compose down && docker compose up -d`.

---

## 4. Sécurité TLS & WAF

| Paramètre Cloudflare | Valeur recommandée                                               |
| -------------------- | ---------------------------------------------------------------- |
| SSL mode             | **Full (strict)** <br>*(cert LE à installer côté VPS si besoin)* |
| Always Use HTTPS     | **On**                                                           |
| HSTS                 | facultatif (max-age ≥ 6 mois après rodage)                       |
| Rate Limiting        | 1 000 req / 10 s pour `/api/*`                                   |
| Bot Fight Mode       | On                                                               |

---

## 5. Procédures d’exploitation

### 5.1 Démarrage / arrêt

```bash
# Démarrer toute la stack
cd ~/sentra_core_mem && docker compose up -d
# Arrêt propre
docker compose down
```

### 5.2 Logs rapides

```bash
docker compose logs -f sentra_api      # API
docker compose logs -f sentra_n8n      # n8n
docker compose logs -f cloudflared     # tunnel
```

### 5.3 Sauvegarde n8n

```bash
tar czf /backup/n8n_$(date +%F).tar.gz n8n_data/
```

---

## 6. Dépannage rapide

| Symptôme                                     | Vérif. 1                                                     | Vérif. 2                                                      | Correctif                             |
| -------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- | ------------------------------------- |
| Erreur **1033** Cloudflare                   | `docker compose logs cloudflared` → connexions quittent      | `nslookup <host>` pointe‑t‑il bien vers \*.cfargotunnel.com ? | Revoir CNAME + restart cloudflared    |
| `502` Bad Gateway                            | `curl -I http://sentra_n8n:5678` depuis un conteneur BusyBox | Port exposé dans compose ?                                    | Rebuild n8n / revérifier healthcheck  |
| `schannel CRYPT_E_NO_REVOCATION_CHECK` (Win) | SSL Labs note ≥ B ?                                          | Mode SSL Cloudflare                                           | Forcer TLS 1.2+, corriger chaîne cert |

---

## 7. Références & liens utiles

* Cloudflare Tunnel doc : [https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
* n8n Docker : [https://docs.n8n.io/hosting/docker/](https://docs.n8n.io/hosting/docker/)
* OVH VPS firewall : [https://docs.ovh.com/fr/vps/configurer-firewall-network/](https://docs.ovh.com/fr/vps/configurer-firewall-network/)
* Repo Git SENTRA_CORE_MEM : *à compléter*

---

> **Rappel :** Toute modification du fichier `cloudflared/config.yml` → `docker compose restart cloudflared` puis vérification **SAIN** dans Zero Trust.

---

© 2025 SENTRA_CORE_MEM · Licence CC‑BY‑SA
