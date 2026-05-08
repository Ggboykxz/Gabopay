# GABOPAY — agents.md

> Infrastructure de paiement unifiée pour le marché gabonais et africain.
> Stack : Next.js 15 · FastAPI · React Native/Expo · PostgreSQL · Redis · Docker

---

## 🧠 IDENTITÉ DU PROJET

GABOPAY est un **Payment Infrastructure SaaS B2B** — le "Stripe du Gabon".
Il unifie Airtel Money, Moov Money, cartes bancaires (VISA/Mastercard) et paiements en espèces
(réseau d'agents) dans une seule API REST + SDK multi-langage.

**Cible primaire :** Développeurs et entreprises gabonaises ayant besoin d'intégrer des paiements.
**Cible secondaire :** Marchands e-commerce, SaaS locaux, NGOs, administrations publiques.
**Expansion :** Cameroun → Congo → Tchad → Sénégal

---

## 🏗️ ARCHITECTURE GLOBALE

```
gabopay/
├── apps/
│   ├── api/              # FastAPI — Core Payment Engine
│   ├── dashboard/        # Next.js 15 — Portail marchand
│   ├── docs/             # Next.js 15 — Documentation développeur
│   └── mobile/           # Expo React Native — App marchands mobile
├── packages/
│   ├── sdk-js/           # SDK JavaScript/TypeScript (npm)
│   ├── sdk-python/       # SDK Python (pypi)
│   ├── sdk-flutter/      # SDK Flutter (pub.dev)
│   └── shared/           # Types, constantes, utilitaires partagés
├── infrastructure/
│   ├── docker/           # Docker Compose dev/prod
│   ├── nginx/            # Reverse proxy config
│   └── scripts/          # Scripts de déploiement
└── agents.md             # Ce fichier
```

---

## 🤖 AGENTS ET LEURS RÔLES

### AGENT 1 — `api-agent`
**Rôle :** Backend FastAPI — moteur de paiement central

**Responsabilités :**
- Implémenter tous les endpoints REST (charges, refunds, payouts, webhooks)
- Intégrer les providers : Airtel Money API, Moov Money API, Stripe (cartes)
- Gestion des transactions avec état machine (PENDING → PROCESSING → SUCCESS/FAILED)
- Génération et validation des API Keys (format `gp_live_xxx` / `gp_test_xxx`)
- Signature HMAC des webhooks sortants
- Rate limiting par API key (Redis)
- Idempotency keys pour éviter les doubles charges
- Réconciliation automatique (cron toutes les heures)

**Stack :**
```
FastAPI + Pydantic v2
PostgreSQL (asyncpg + SQLAlchemy 2.0)
Redis (cache + rate limit + idempotency)
Celery + Redis (tâches async : webhooks, réconciliation)
httpx (appels providers)
python-jose (JWT auth dashboard)
```

**Fichiers clés à générer en priorité :**
```
apps/api/
├── main.py
├── core/
│   ├── config.py          # Settings Pydantic (env vars)
│   ├── security.py        # API key hashing, HMAC signature
│   └── database.py        # Async engine + sessions
├── models/
│   ├── merchant.py        # Merchant, ApiKey, WebhookEndpoint
│   ├── transaction.py     # Transaction, Refund, Payout
│   └── provider.py        # ProviderAccount (Airtel, Moov, Card)
├── api/v1/
│   ├── charges.py         # POST /v1/charges, GET /v1/charges/{id}
│   ├── refunds.py         # POST /v1/refunds
│   ├── payouts.py         # POST /v1/payouts
│   ├── webhooks.py        # POST /v1/webhooks (enregistrement)
│   └── balance.py         # GET /v1/balance
├── providers/
│   ├── base.py            # Interface abstraite BaseProvider
│   ├── airtel.py          # Airtel Money Gabon integration
│   ├── moov.py            # Moov Money Gabon integration
│   └── card.py            # Stripe/CinetPay cards integration
├── workers/
│   ├── webhook_dispatcher.py
│   └── reconciliation.py
└── migrations/            # Alembic
```

**Règles strictes :**
- Toute transaction est créée en DB AVANT d'appeler le provider
- Jamais de montant en float → utiliser des entiers (centimes FCFA)
- Chaque appel provider a un timeout de 30s et 3 retries avec backoff exponentiel
- Les credentials providers sont chiffrés en DB (Fernet)
- Les logs ne contiennent JAMAIS de numéros de téléphone ou données personnelles en clair

---

### AGENT 2 — `dashboard-agent`
**Rôle :** Portail web marchand (Next.js 15 App Router)

**Responsabilités :**
- Auth marchands (email/password + 2FA TOTP)
- Onboarding KYC (upload docs, validation manuelle)
- Tableau de bord : volume, revenus, taux de succès, graphiques
- Gestion des transactions (liste, détail, remboursement)
- Gestion des API Keys (créer, révoquer, copier)
- Configuration webhooks (URL, events, secret, logs de livraison)
- Paramètres du compte, profil, équipe (rôles admin/dev/viewer)
- Mode test vs live (switch visible dans le header)

**Stack :**
```
Next.js 15 (App Router, Server Components)
TailwindCSS v4
shadcn/ui (composants)
Recharts (graphiques)
React Hook Form + Zod
SWR (data fetching client)
next-auth v5
```

**Design system :**
- Couleurs : Vert Gabon (#009e60) comme accent principal, fond dark (#0a0a0a) ou light blanc
- Police : Geist Mono pour les codes/API keys, Inter Display pour le reste
- Inspiré de : Stripe Dashboard (densité d'info) + Vercel (simplicité)

**Pages à implémenter dans l'ordre :**
```
1. /login, /register, /verify-email
2. /dashboard → métriques principales
3. /dashboard/transactions → table avec filtres
4. /dashboard/transactions/[id] → détail
5. /dashboard/developers/api-keys
6. /dashboard/developers/webhooks
7. /dashboard/developers/webhooks/[id]/logs
8. /dashboard/payouts
9. /dashboard/settings/profile
10. /dashboard/settings/team
```

---

### AGENT 3 — `sdk-agent`
**Rôle :** SDKs officiels multi-langage

**Responsabilités :**
- SDK JS/TS (Node.js + browser) → `npm install gabopay`
- SDK Python → `pip install gabopay`
- SDK Flutter/Dart → `pub add gabopay`
- Chaque SDK doit couvrir : Charges, Refunds, Webhooks (vérification signature), Balance

**SDK JS — structure :**
```typescript
// Usage cible
import Gabopay from 'gabopay';

const gp = new Gabopay('gp_live_sk_xxx');

const charge = await gp.charges.create({
  amount: 5000,        // en FCFA (entier)
  currency: 'XAF',
  method: 'airtel_money',
  phone: '+24177000000',
  description: 'Commande #123',
  metadata: { orderId: '123' }
});

// Vérification webhook
const event = gp.webhooks.constructEvent(
  rawBody,
  signature,
  webhookSecret
);
```

**Règles SDK :**
- Retry automatique sur erreurs réseau (3 tentatives, backoff)
- Timeout configurable (défaut 60s)
- Types TypeScript exhaustifs exportés
- Zéro dépendance externe pour le SDK JS (fetch natif)
- Tests unitaires avec mocks pour chaque méthode

---

### AGENT 4 — `docs-agent`
**Rôle :** Site de documentation développeur

**Responsabilités :**
- Landing page de GABOPAY (hero, pricing, use cases)
- Quickstart (5 min → premier paiement)
- Référence API complète (auto-générée depuis OpenAPI + enrichie)
- Guides : intégration Airtel Money, webhooks, mode test, gestion erreurs
- Playground interactif (tester les endpoints avec sa clé test)
- Changelog

**Stack :** Next.js 15 + MDX + Fumadocs ou Nextra

---

### AGENT 5 — `mobile-agent`
**Rôle :** Application mobile marchands (Expo React Native)

**Responsabilités :**
- Dashboard résumé : solde, volume du jour
- Scanner QR code pour initier un paiement en caisse
- Notifications push (transaction reçue)
- Historique transactions
- Demande de payout rapide

**Stack :** Expo SDK 52, React Native, NativeWind, Zustand, Expo Router

---

### AGENT 6 — `infra-agent`
**Rôle :** Infrastructure et DevOps

**Responsabilités :**
- `docker-compose.yml` pour dev local (api, dashboard, postgres, redis, celery)
- `docker-compose.prod.yml` pour production (+ nginx, SSL certbot)
- Variables d'environnement : `.env.example` exhaustif
- Scripts de setup : `./scripts/setup.sh`, `./scripts/deploy.sh`
- GitHub Actions CI/CD :
  - Lint + tests sur chaque PR
  - Deploy automatique sur push `main` → VPS Oracle Cloud / Render

---

## 📊 MODÈLE DE DONNÉES PRINCIPAL

```sql
-- Marchands
merchants (id, name, email, phone, country, status, kyc_status, created_at)
api_keys (id, merchant_id, name, key_hash, prefix, mode[test|live], last_used_at, revoked_at)
webhook_endpoints (id, merchant_id, url, events[], secret_hash, active)

-- Transactions
transactions (
  id UUID PK,
  merchant_id UUID FK,
  amount INTEGER NOT NULL,          -- en centimes FCFA
  currency CHAR(3) DEFAULT 'XAF',
  method ENUM(airtel_money, moov_money, card, cash),
  status ENUM(pending, processing, succeeded, failed, refunded),
  phone VARCHAR(20),
  provider_ref VARCHAR(100),        -- ref côté Airtel/Moov
  idempotency_key VARCHAR(100) UNIQUE,
  metadata JSONB,
  error_code VARCHAR(50),
  error_message TEXT,
  mode ENUM(test, live),
  created_at, updated_at
)

refunds (id, transaction_id, amount, status, reason, created_at)
payouts (id, merchant_id, amount, method, phone, status, created_at)

-- Comptabilité
merchant_balances (merchant_id, available_amount, pending_amount, updated_at)
balance_transactions (id, merchant_id, type, amount, fee, net, related_id, created_at)

-- Audit
webhook_deliveries (id, endpoint_id, event_type, payload, response_status, attempt, created_at)
```

---

## 💰 MODÈLE TARIFAIRE (à implémenter dans l'API)

```python
FEES = {
    "airtel_money": {
        "percentage": 1.5,   # 1.5% du montant
        "fixed": 0,          # pas de frais fixe
        "min": 50,           # 50fcfa minimum
    },
    "moov_money": {
        "percentage": 1.5,
        "fixed": 0,
        "min": 50,
    },
    "card": {
        "percentage": 2.9,
        "fixed": 100,        # +100fcfa fixe
        "min": 150,
    }
}

SUBSCRIPTION_PLANS = {
    "starter": {
        "price_monthly_xaf": 10_000,
        "transaction_limit": 500,
        "team_members": 1,
    },
    "growth": {
        "price_monthly_xaf": 35_000,
        "transaction_limit": 5000,
        "team_members": 5,
    },
    "scale": {
        "price_monthly_xaf": 100_000,
        "transaction_limit": None,  # illimité
        "team_members": None,
        "custom_fee_negotiable": True,
    }
}
```

---

## 🔐 SÉCURITÉ — RÈGLES NON NÉGOCIABLES

1. **API Keys** : jamais stockées en clair → SHA-256 en DB, préfixe `gp_live_` ou `gp_test_` lisible
2. **Webhooks** : signature HMAC-SHA256 sur chaque payload, timestamp anti-replay (5 min)
3. **Credentials providers** : chiffrés Fernet (AES-128-CBC) en DB
4. **Auth dashboard** : JWT access (15min) + refresh token (30j) + rotation
5. **Rate limiting** : 100 req/min par API key (Redis sliding window)
6. **Idempotency** : toute création de charge accepte `Idempotency-Key` header
7. **PCI-DSS light** : on ne touche JAMAIS aux numéros de carte → délégué à Stripe/CinetPay
8. **Logs** : masquer phone, email, amounts dans les logs de debug (pas en prod)
9. **HTTPS only** : redirect HTTP → HTTPS strict en production
10. **CORS** : whitelist des domaines marchands enregistrés uniquement

---

## 🔄 FLUX DE PAIEMENT (Airtel Money exemple)

```
Client App ──POST /v1/charges──► GABOPAY API
                                     │
                           1. Vérifier API key + mode
                           2. Calculer fees
                           3. Créer transaction en DB (PENDING)
                           4. Appeler Airtel Money API
                                     │
                              Airtel Money
                           ┌──────────────────┐
                           │ USSD push → client│
                           │ Client confirme   │
                           │ Airtel → callback │
                           └──────────────────┘
                                     │
                           5. Callback reçu → update DB (SUCCESS/FAILED)
                           6. Dispatch webhook vers marchand
                           7. Update balance marchand
                                     │
Client App ◄──── webhook ──── Marchand App
```

---

## 🛠️ ORDRE DE DÉVELOPPEMENT

### Phase 1 — MVP (Semaines 1-4)
- [ ] Schéma DB complet + migrations Alembic
- [ ] Auth API keys (create, validate, revoke)
- [ ] Endpoint `POST /v1/charges` (Airtel Money uniquement, mode test)
- [ ] Webhook dispatcher (Celery)
- [ ] Dashboard : login + liste transactions basique
- [ ] SDK JS minimal (charges + webhook verify)

### Phase 2 — Core complet (Semaines 5-8)
- [ ] Intégration Moov Money
- [ ] Intégration cartes (CinetPay ou Stripe)
- [ ] Refunds + Payouts
- [ ] Balance & balance_transactions
- [ ] Dashboard complet (API keys, webhooks, analytics)
- [ ] Mode test entièrement fonctionnel avec données simulées

### Phase 3 — Go-to-market (Semaines 9-12)
- [ ] SDK Python + Flutter
- [ ] Site docs + Quickstart
- [ ] KYC flow (onboarding marchand)
- [ ] Facturation abonnements (Stripe Billing pour facturer les marchands)
- [ ] App mobile marchands (Expo)
- [ ] Dashboard analytics avancé (Recharts)

### Phase 4 — Scale (Mois 4+)
- [ ] Multi-pays (Cameroun : Orange Money, MTN)
- [ ] API Links (liens de paiement sans code)
- [ ] Terminal virtuel (paiement manuel depuis dashboard)
- [ ] Rapports comptables export CSV/PDF
- [ ] Programme partenaires développeurs

---

## ⚙️ VARIABLES D'ENVIRONNEMENT REQUISES

```env
# App
APP_ENV=development          # development | production
SECRET_KEY=                  # 32 bytes random hex
ENCRYPTION_KEY=              # Fernet key (base64)

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/gabopay
REDIS_URL=redis://localhost:6379/0

# Providers
AIRTEL_BASE_URL=https://openapi.airtel.africa
AIRTEL_CLIENT_ID=
AIRTEL_CLIENT_SECRET=
AIRTEL_CALLBACK_URL=https://api.gabopay.ga/v1/callbacks/airtel

MOOV_BASE_URL=
MOOV_API_KEY=
MOOV_CALLBACK_URL=https://api.gabopay.ga/v1/callbacks/moov

CINETPAY_API_KEY=
CINETPAY_SITE_ID=

# Dashboard auth
JWT_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (KYC notifications, receipts)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@gabopay.ga

# Fees & Limits
PLATFORM_FEE_PERCENTAGE=1.5
MIN_CHARGE_AMOUNT=500        # 500fcfa minimum
MAX_CHARGE_AMOUNT=5000000    # 5mfcfa maximum
```

---

## 📋 CONVENTIONS DE CODE

### Commits (one commit per change — règle stricte)
```
feat(charges): add Airtel Money provider integration
fix(webhooks): retry on 5xx response from merchant endpoint
refactor(models): move fee calculation to Transaction model method
test(sdk): add unit tests for webhook signature verification
docs(api): update charges endpoint OpenAPI description
chore(infra): add nginx SSL config for production
```

### Nommage
- **Endpoints API** : snake_case pour query params, camelCase interdit dans les JSON de réponse
- **Variables Python** : snake_case strict
- **Composants React** : PascalCase
- **Tables DB** : snake_case pluriel (`transactions`, `api_keys`)
- **Constantes** : UPPER_SNAKE_CASE

### Réponses API — format uniforme
```json
{
  "id": "ch_01j7xxxxx",
  "object": "charge",
  "amount": 5000,
  "currency": "XAF",
  "status": "succeeded",
  "created": 1720000000
}
```

### Erreurs API — format uniforme
```json
{
  "error": {
    "code": "insufficient_funds",
    "message": "Le compte Airtel Money ne dispose pas de fonds suffisants.",
    "type": "provider_error",
    "doc_url": "https://docs.gabopay.ga/errors#insufficient_funds"
  }
}
```

---

## 🧪 STRATÉGIE DE TEST

- **Mode test** : toutes les charges en mode `gp_test_sk_xxx` sont simulées → pas d'appel provider réel
- **Numéros spéciaux en mode test** :
  - `+24100000001` → toujours SUCCESS
  - `+24100000002` → toujours FAILED (insufficient_funds)
  - `+24100000003` → timeout simulé (30s)
- **Tests unitaires** : pytest pour tous les services métier
- **Tests d'intégration** : TestClient FastAPI avec DB PostgreSQL de test
- **Coverage cible** : > 80% sur `providers/`, `core/security.py`, `workers/`

---

## 📱 INTÉGRATION SDK — EXEMPLE RAPIDE

```javascript
// Node.js — Intégration en 10 lignes
const Gabopay = require('gabopay');
const gp = new Gabopay(process.env.GABOPAY_SECRET_KEY);

app.post('/checkout', async (req, res) => {
  const charge = await gp.charges.create({
    amount: 10000,           // 10 000fcfa
    currency: 'XAF',
    method: 'airtel_money',
    phone: req.body.phone,
    description: `Commande #${req.body.orderId}`,
  });
  res.json({ chargeId: charge.id, status: charge.status });
});

// Webhook handler
app.post('/webhook/gabopay', (req, res) => {
  const event = gp.webhooks.constructEvent(
    req.rawBody,
    req.headers['gp-signature'],
    process.env.GABOPAY_WEBHOOK_SECRET
  );
  if (event.type === 'charge.succeeded') {
    fulfillOrder(event.data.metadata.orderId);
  }
  res.sendStatus(200);
});
```

---

## 🎯 MÉTRIQUES DE SUCCÈS (KPIs)

| Métrique | Cible 6 mois | Cible 12 mois |
|---|---|---|
| Marchands actifs | 50 | 300 |
| Volume mensuel traité | 50mfcfa | 500mfcfa |
| Revenu mensuel (fees) | 750kfcfa | 7.5mfcfa |
| Taux de succès transactions | > 95% | > 97% |
| Temps de réponse API p99 | < 2s | < 1s |
| Uptime | 99.5% | 99.9% |

---

*GABOPAY — Built in Gabon, pour l'Afrique. 🇬🇦*