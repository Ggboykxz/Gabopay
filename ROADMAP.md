# GABOPAY Roadmap

Cette roadmap décrit les jalons de développement du projet GABOPAY.

---

## 🎯 Vision

Devenir l'infrastructure de paiement de référence pour l'Afrique centrale, unissant tous les providers de mobile money et cartes bancaires dans une API unifiée.

---

## 📅 Timeline

### Phase 1: MVP (Semaines 1-4) ✅ TERMINÉ

**Objectif:** Fondamentaux opérationnels

- [x] Schéma DB complet + migrations SQLAlchemy
- [x] Auth API keys (create, validate, revoke)
- [x] Endpoint `POST /v1/charges` (Airtel Money uniquement, mode test)
- [x] Webhook dispatcher (Celery)
- [x] Dashboard : login + liste transactions basique
- [x] SDK JS minimal (charges + webhook verify)

**Livrables:**
- API fonctionnelle avec mode test
- Dashboard basique opérationnel

---

### Phase 2: Core Complet (Semaines 5-8) 🚧 EN COURS

**Objectif:** Ensemble des fonctionnalités core

- [ ] Intégration Moov Money complète
- [ ] Intégration cartes (CinetPay ou Stripe)
- [ ] Refunds + Payouts complets
- [ ] Balance & balance_transactions
- [ ] Dashboard complet (API keys, webhooks, analytics)
- [ ] Mode test avec toutes les模拟

**Livrables:**
- Tous les providers actifs
- Payouts fonctionnels
- Dashboard complet

---

### Phase 3: Go-to-Market (Semaines 9-12) 📋 PLANIFIÉ

**Objectif:** Préparation commercialisation

- [ ] SDK Python complet
- [ ] SDK Flutter/Dart
- [ ] Site docs + Quickstart complet
- [ ] KYC flow (onboarding marchand)
- [ ] Facturation abonnements
- [ ] App mobile marchands complète

**Livrables:**
- SDKs multi-plateforme
- Documentation développeur complète
- App mobile fonctionnelle

---

### Phase 4: Scale (Mois 4+) 🔭 VISION

**Objectif:** Expansion régionale

- [ ] Multi-pays (Cameroun: Orange Money, MTN)
- [ ] API Links (liens de paiement sans code)
- [ ] Terminal virtuel (paiement manuel dashboard)
- [ ] Rapports comptables export CSV/PDF
- [ ] Programme partenaires développeurs

---

## 🛤️ Jalons Techniques

### Infrastructure

| Jalon | Description | Status |
|-------|-------------|--------|
| Docker Compose Dev | Environment local complet | ✅ |
| Docker Compose Prod | Environment production | ✅ |
| CI/CD Pipeline | GitHub Actions | ✅ |
| Monitoring | Logs, métriques | 📋 |
| SSL/TLS | HTTPS obligatoire | ✅ |

### API

| Endpoint | Status |
|----------|--------|
| Charges | ✅ |
| Refunds | ✅ |
| Payouts | ✅ |
| Balance | ✅ |
| Webhooks | ✅ |
| Auth JWT | ✅ |

### Providers

| Provider | Mode Test | Mode Prod |
|----------|-----------|-----------|
| Airtel Money | ✅ | 🚧 |
| Moov Money | ✅ | 🚧 |
| Card (CinetPay) | ✅ | 🚧 |

---

## 🔮 Vision Long Terme

### 2026 (Année 1)
- 50 marchands actifs
- Volume mensuel: 50M XAF
- Couverture Gabon 100%

### 2027 (Année 2)
- 300 marchands actifs
- Expansion Cameroun, Congo
- Volume mensuel: 500M XAF

### 2028 (Année 3)
- Multi-pays Afrique centrale
- 1000+ marchands
- Partenariats banques

---

## 📊 Priorités

1. **Stabilité** — Uptime >99.5%
2. **Sécurité** — PCI-DSS compliant
3. **DX** — Documentation, SDKs
4. **Expansion** — Nouveaux pays

---

*Dernière mise à jour: Mai 2026*