# GABOPAY — Payment Infrastructure for Africa

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Stack-FastAPI%20%2B%20Next.js-orange" alt="Stack">
  <img src="https://img.shields.io/badge/Country-Gabon-red" alt="Gabon">
</p>

> **GABOPAY** est l'infrastructure de paiement unifiée pour le Gabon et l'Afrique. Le "Stripe du Gabon" — unifie Airtel Money, Moov Money, cartes bancaires (VISA/Mastercard) et paiements en espèces dans une seule API REST + SDK multi-langage.

---

## 📋 Table des Matières

1. [ Présentation ](#présentation)
2. [ Architecture ](#architecture)
3. [ Installation Rapide ](#installation-rapide)
4. [ API Reference ](#api-reference)
5. [ SDKs Officiels ](#sdks-officiels)
6. [ Configuration ](#configuration)
7. [ Déploiement ](#déploiement)
8. [ Design System ](#design-system)
9. [ Contribution ](#contribution)
10. [ Licence ](#licence)

---

## 🏛️ Présentation

### Cible

- **Primaire:** Développeurs et entreprises gabonaises ayant besoin d'intégrer des paiements
- **Secondaire:** Marchands e-commerce, SaaS locaux, NGOs, administrations publiques
- **Expansion:** Cameroun → Congo → Tchad → Sénégal

### Fonctionnalités Principales

| Feature | Description |
|---------|-------------|
| **Multi-method Payments** | Airtel Money, Moov Money, Cartes (VISA/Mastercard), Espèces |
| **API REST** | Endpoints standardisés pour charges, refunds, payouts |
| **SDKs Multi-langage** | JavaScript/TypeScript, Python, Flutter |
| **Mode Test** | Numéros de test pour simulation sans frais |
| **Webhooks** | Notifications temps réel pour tous les événements |
| **Dashboard Marchand** | Gestion des transactions, clés API, webhooks |
| **KYC Integration** | Onboarding marchands avec vérification identité |

### Métriques

| Métrique | Cible 6 mois | Cible 12 mois |
|----------|--------------|---------------|
| Marchands actifs | 50 | 300 |
| Volume mensuel | 50M XAF | 500M XAF |
| Revenu mensuel (fees) | 750K XAF | 7.5M XAF |
| Taux de succès | >95% | >97% |
| Uptime | 99.5% | 99.9% |

---

## 🏗️ Architecture Globale

```
gabopay/
├── apps/
│   ├── api/              # FastAPI — Moteur de paiement central
│   ├── dashboard/         # Next.js 15 — Portail marchand
│   ├── docs/             # Next.js 15 — Documentation développeur
│   └── mobile/           # Expo React Native — App marchands
├── packages/
│   ├── sdk-js/           # SDK JavaScript/TypeScript
│   ├── sdk-python/       # SDK Python
│   └── shared/           # Types, tokens, utilitaires partagés
├── infrastructure/
│   ├── docker/           # Docker Compose
│   ├── nginx/            # Reverse proxy avec SSL
│   └── scripts/          # Scripts déploiement
└── DESIGN.md            # Système de design
```

### Stack Technique

| Couche | Technologie |
|--------|-------------|
| **Backend** | FastAPI + Pydantic v2 + SQLAlchemy 2.0 |
| **Base de données** | PostgreSQL 16 (asyncpg) |
| **Cache/Sessions** | Redis 7 |
| **Tâches async** | Celery + Redis |
| **Frontend Web** | Next.js 15 (App Router) + TailwindCSS |
| **Mobile** | Expo SDK 52 + React Native |
| **Containerisation** | Docker + Docker Compose |

---

## 🚀 Installation Rapide

### Prérequis

```bash
# Node.js 18+
node --version  # ≥ 18.0.0

# Python 3.11+
python3 --version  # ≥ 3.11

# Docker & Docker Compose
docker --version
docker-compose --version

# PostgreSQL 16 (optionnel, peut utiliser Docker)
```

### 1. Clone du projet

```bash
git clone https://github.com/Ggboykxz/Gabopay.git
cd Gabopay
```

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables (voir section Configuration)
```

### 3. Démarrage avec Docker

```bash
# Mode développement
./infrastructure/scripts/setup.sh
docker-compose -f infrastructure/docker/docker-compose.yml up

# Ou directement
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

Les services seront disponibles sur:
- **API:** http://localhost:8000
- **Dashboard:** http://localhost:3000
- **Docs:** http://localhost:3001

### 4. Démarrage manuel (sans Docker)

#### Backend (FastAPI)

```bash
# Installation des dépendances Python
cd apps/api
pip install poetry
poetry install

# Lancement
poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Next.js)

```bash
# Installation des dépendances Node.js
npm install

# Lancement dashboard
cd apps/dashboard
npm run dev

# Lancement docs
cd apps/docs
npm run dev
```

---

## 📡 API Reference

### Base URL

```
Production: https://api.gabopay.ga/v1
Développement: http://localhost:8000/v1
```

### Authentication

Toutes les requêtes nécessitent une API Key dans le header:

```bash
curl -X GET https://api.gabopay.ga/v1/charges \
  -H "X-API-Key: gp_test_sk_xxxxxxxx"
```

### Endpoints

#### ⚡ Charges (Payments)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/charges` | Créer un paiement |
| `GET` | `/charges/{id}` | Récupérer une charge |
| `GET` | `/charges` | Liste des charges |

**Créer une charge:**

```bash
curl -X POST https://api.gabopay.ga/v1/charges \
  -H "X-API-Key: gp_test_sk_xxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "currency": "XAF",
    "method": "airtel_money",
    "phone": "+24177000000",
    "description": "Commande #123"
  }'
```

**Réponse:**

```json
{
  "id": "ch_01J7XXXXX",
  "object": "charge",
  "amount": 5000,
  "currency": "XAF",
  "status": "succeeded",
  "method": "airtel_money",
  "phone": "+24177••••••",
  "description": "Commande #123",
  "fee_amount": 75,
  "created": 1720000000
}
```

#### 💸 Refunds

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/refunds/{transaction_id}` | Créer un remboursement |

#### 💰 Payouts

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/payouts` | Créer un retrait |
| `GET` | `/payouts` | Liste des payouts |

#### ⚖️ Balance

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/balance` | Solde du marchand |
| `GET` | `/balance/transactions` | Historique des transactions |

#### 🪝 Webhooks

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/webhooks` | Créer un endpoint webhook |
| `GET` | `/webhooks` | Liste des webhooks |
| `GET` | `/webhooks/{id}/deliveries` | Logs de livraison |

### Codes d'Erreur

| Code | Description |
|------|-------------|
| `insufficient_funds` | Funds insuffisants sur le compte mobile |
| `invalid_phone` | Numéro de téléphone invalide |
| `timeout` | Délai d'attente dépassé |
| `provider_error` | Erreur du provider de paiement |
| `rate_limit_exceeded` | Limite de requêtes atteinte |

### Mode Test

Les clés API commençant par `gp_test_` utilisent le mode simulation:

| Numéro | Résultat |
|--------|-----------|
| `+24100000001` | Toujours SUCCESS |
| `+24100000002` | Toujours FAILED (insufficient_funds) |
| `+24100000003` | Timeout (30s) |

---

## 🛠️ SDKs Officiels

### JavaScript / TypeScript

```bash
npm install gabopay
```

```typescript
import Gabopay from 'gabopay';

const gp = new Gabopay('gp_test_sk_xxxxxxxx');

// Créer un paiement
const charge = await gp.charges.create({
  amount: 5000,        // 5,000 XAF
  currency: 'XAF',
  method: 'airtel_money',
  phone: '+24177000000',
  description: 'Commande #123'
});

// Vérifier un webhook
const event = gp.webhooks.constructEvent(
  rawBody,
  signature,
  webhookSecret
);
```

### Python

```bash
pip install gabopay
```

```python
from gabopay import Gabopay

gp = Gabopay(secret_key='gp_test_sk_xxxxxxxx')

# Créer un paiement
charge = gp.charges_create({
    'amount': 5000,
    'currency': 'XAF',
    'method': 'airtel_money',
    'phone': '+24177000000',
    'description': 'Commande #123'
})

# Vérifier un webhook
event = Gabopay.construct_webhook_event(
    payload=payload,
    signature=signature,
    secret=webhook_secret
)
```

---

## ⚙️ Configuration

### Variables d'Environnement

```env
# ===========================================
# APPLICATION
# ===========================================
APP_ENV=development                    # development | production
SECRET_KEY=your-secret-key-here      # 32 bytes minimum
ENCRYPTION_KEY=your-encryption-key    # Fernet key (base64)

# ===========================================
# BASE DE DONNÉES
# ===========================================
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/gabopay
REDIS_URL=redis://localhost:6379/0

# ===========================================
# PROVIDERS DE PAIEMENT
# ===========================================
# Airtel Money
AIRTEL_BASE_URL=https://openapi.airtel.africa
AIRTEL_CLIENT_ID=
AIRTEL_CLIENT_SECRET=
AIRTEL_CALLBACK_URL=https://api.gabopay.ga/v1/callbacks/airtel

# Moov Money
MOOV_BASE_URL=https://api.moov.africa
MOOV_API_KEY=
MOOV_CALLBACK_URL=https://api.gabopay.ga/v1/callbacks/moov

# CinetPay (Cartes)
CINETPAY_API_KEY=
CINETPAY_SITE_ID=

# ===========================================
# AUTHENTIFICATION DASHBOARD
# ===========================================
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# ===========================================
# EMAILS (optionnel)
# ===========================================
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@gabopay.ga

# ===========================================
# FRAIS & LIMITES
# ===========================================
PLATFORM_FEE_PERCENTAGE=1.5
MIN_CHARGE_AMOUNT=500        # 500 XAF minimum
MAX_CHARGE_AMOUNT=5000000    # 5,000,000 XAF maximum
```

### Frais de Transaction

| Méthode | Pourcentage | Frais fixe | Minimum |
|---------|-------------|------------|---------|
| Airtel Money | 1.5% | 0 XAF | 50 XAF |
| Moov Money | 1.5% | 0 XAF | 50 XAF |
| Carte | 2.9% | 100 XAF | 150 XAF |

---

## 🚢 Déploiement

### Développement Local

```bash
# Avec Docker Compose
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Avec scripts
./infrastructure/scripts/setup.sh
```

### Production

```bash
# Préparation
cp .env.example .env.production
# Éditer toutes les variables avec les valeurs de prod

# Déploiement
./infrastructure/scripts/deploy.sh production
```

### Docker Production

```yaml
# infrastructure/docker/docker-compose.prod.yml
services:
  postgres:
    image: postgres:16-alpine
    # ...

  redis:
    image: redis:7-alpine
    # ...

  api:
    build: ./apps/api
    environment:
      - APP_ENV=production
      - DATABASE_URL=...
    # ...

  dashboard:
    build: ./apps/dashboard
    # ...

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

### Configuration Nginx (SSL)

```nginx
server {
    listen 443 ssl http2;
    server_name api.gabopay.ga;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://api:8000;
        # ... headers
    }
}
```

---

## 🎨 Design System

Le système de design GABOPAY est documenté dans [DESIGN.md](./DESIGN.md).

### Couleurs Principales

| Token | Valeur | Usage |
|-------|--------|-------|
| `brand` | `#009e60` | Vert Gabon — couleur principale |
| `bg.base` | `#0a0b0c` | Fond sombre principal |
| `bg.surface` | `#111214` | Cartes, panels |
| `text.primary` | `#f1f3f5` | Titres, montants |
| `success` | `#009e60` | Transactions réussies |
| `error` | `#fa5252` | Transactions échouées |
| `warning` | `#fcc419` | En attente |

### Composants Clés

- **TransactionBadge** — Badge de statut (succeeded, failed, pending, processing, refunded)
- **MetricCard** — Carte KPI dashboard
- **DataTable** — Tableau de transactions
- **APIKeyCard** — Carte clé API
- **AmountDisplay** — Affichage montants (jamais de décimales en XAF)

### Règles Importantes

✓ Montants toujours en `font-mono`, pas de décimales (XAF est un entier)  
✓ Couleur brand uniquement `#009e60`  
✓ Fond de carte `#111214`  
✓ Animations max 300ms  

---

## 🤝 Contribution

### Prérequis

```bash
# Node.js 18+
# Python 3.11+
# Docker
```

### Setup Development

```bash
# Installation complète
npm install
poetry install

# Configuration pre-commit
npm run lint
poetry run ruff check
```

### Structure des Commits

```
feat(charges): add Airtel Money provider integration
fix(webhooks): retry on 5xx response
refactor(models): move fee calculation
test(sdk): add webhook signature verification
docs(api): update endpoint description
chore(infra): add nginx SSL config
```

### Tests

```bash
# Python
poetry run pytest --cov=apps/api

# JavaScript
npm run test --workspace=packages/sdk-js
```

---

## 📄 Licence

MIT License — Voir [LICENSE](./LICENSE)

---

## 🇬🇦 GABOPAY

*Built in Gabon, pour l'Afrique.*

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red" alt="Made with love">
  <img src="https://img.shields.io/badge/Location-Libreville%2C%20Gabon-blue" alt="Location">
</p>