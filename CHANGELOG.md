# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr-FR/1.0.0/).

---

## [1.0.0] - 2026-05-08

### Added

#### Backend (FastAPI)
- **API REST complète** avec endpoints pour:
  - Charges (payments): `POST /v1/charges`, `GET /v1/charges/{id}`, `GET /v1/charges`
  - Refunds: `POST /v1/refunds/{id}`
  - Payouts: `POST /v1/payouts`, `GET /v1/payouts`
  - Balance: `GET /v1/balance`, `GET /v1/balance/transactions`
  - Webhooks: `POST /v1/webhooks`, `GET /v1/webhooks`, `GET /v1/webhooks/{id}/deliveries`
  - Auth: `POST /v1/auth/register`, `POST /v1/auth/login`, `POST /v1/auth/refresh`

- **Providers de paiement:**
  - Airtel Money integration
  - Moov Money integration
  - Card payments (CinetPay/Stripe)
  - Mode test avec numéros spéciaux simulation

- **Models SQLAlchemy:**
  - Merchant, ApiKey, WebhookEndpoint
  - Transaction, Refund, Payout
  - MerchantBalance, BalanceTransaction
  - WebhookDelivery

- **Workers:**
  - Webhook dispatcher (Celery)
  - Reconciliation worker (auto-sync transactions)

#### Frontend (Next.js 15)
- **Dashboard Marchand:**
  - Page overview avec KPIs
  - Liste transactions avec filtres
  - Gestion API Keys
  - Configuration Webhooks
  - Demandes de payout
  - Paramètres profil

#### Documentation (Next.js)
- Page d'accueil GABOPAY
- Quickstart guide
- Référence API complète

#### Mobile (Expo React Native)
- Écran login
- Dashboard avec balance
- Scanner QR code
- Liste transactions

#### SDKs
- **SDK JavaScript/TypeScript:**
  - Charges, Refunds, Webhooks
  - Support Node.js et browser

- **SDK Python:**
  - Charges, Refunds, Webhooks

#### Infrastructure
- Docker Compose (dev + prod)
- Dockerfiles pour chaque service
- Configuration Nginx avec SSL
- GitHub Actions CI/CD
- Scripts de setup et deployment

#### Design System
- Tokens de couleurs (Gabon green #009e60)
- Typographie (Geist Mono, Inter)
- Composants React
- Documentation DESIGN.md complète

### Changed

- Architecture refactorisée pour supporter la Phase 1 MVP
- Configuration centralisée avec Pydantic Settings

### Fixed

- Protection contre les doubles charges (idempotency keys)
- Rate limiting par API key
- Masking des données sensibles dans les logs

---

## [0.0.1] - 2026-05-01

### Added

- Projet initialisé
- Structure de fichiers définie dans agents.md

---

## À venir

### Phase 2 (Prévue)

- Intégration complète Moov Money
- Intégration cartes complète
- Dashboard analytics avancé (Recharts)
- Tests unitaires >80% coverage

### Phase 3 (Prévue)

- SDK Flutter
- Site documentation complet
- KYC flow marchands

---

*Ce projet suit Semantic Versioning. Les versions majeures indiquent des changements incompatibles.*