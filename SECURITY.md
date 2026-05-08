# Security Policy

La sécurité est une priorité absolue pour GABOPAY. Ce document décrit notre politique de sécurité et comment signaler les vulnérabilités.

---

## 🔐 Politique de Sécurité

### Données Sensibles

- **API Keys:** Hachées avec SHA-256 avant stockage en base de données
- **Credentials Providers:** Chiffrés avec Fernet (AES-128-CBC)
- **Tokens JWT:** Signés avec HMAC-SHA256, expiration courte (15min access, 30j refresh)
- **Webhooks:** Signature HMAC-SHA256 avec timestamp anti-replay (5 min)

### Protection

- **Rate Limiting:** 100 req/min par API key (Redis sliding window)
- **CORS:** Whitelist des domaines marchands enregistrés
- **HTTPS Only:** Redirect HTTP → HTTPS en production
- **PCI-DSS Light:** Délégation du stockage des cartes à Stripe/CinetPay

---

## 🐛 Signalement de Vulnérabilités

### Comment signaler

**Ne PAS** créer d'issue publique pour les vulnérabilités de sécurité.

Utilisez plutôt **privément** par email:

```
Email: security@gabopay.ga
Sujet: [SECURITY] Brève description
```

### Ce qu'il faut inclure

1. **Description** de la vulnérabilité
2. **Steps to Reproduce** détaillés
3. **Impact** potentiel
4. **Proof of Concept** si possible
5. **Contact** pour suivi

### Délai de réponse

- **Confirmation:** 24-48h
- **Resolution:** Selon sévérité
  - Critical: 24-48h
  - High: 7 jours
  - Medium: 30 jours
  - Low: 90 jours

---

## 🔧 Exigences de Sécurité pour les Contributeurs

### Code Review

- Au moins 1 approval requise pour merge
- Scan automatique des dépendances (npm audit, pip-audit)
- Tests de sécurité dans CI/CD

### Dependencies

- Mise à jour régulière des dépendances
- Vérification des vulnérabilités connues
- Lock files obligatoires

---

## 📋 Bonnes Pratiques pour les Développeurs

### Ne jamais

❌ Commiter des secrets dans le code  
❌ Stocker des credentials en plaintext  
❌ Utiliser des mots de passe par défaut  
❌ Ignorer les alertes de sécurité  

### Toujours

✓ Utiliser les variables d'environnement pour les secrets  
✓ Valider les entrées utilisateur  
✓ Encoder les sorties pour éviter XSS  
✓ Utiliser des requêtes paramétrées pour éviter SQL injection  

---

## 🔄 Politique de Disclosure

1. **Privé → Vendor:** Signalement direct
2. **Fix → Public:** Après correctif déployé
3. **Timeline:** 90 jours maximum avant publication

---

## 📞 Contact Sécurité

```
Email: security@gabopay.ga
PGP: [Clé PGP à venir]
```

---

*Merci de contribuer à la sécurité de GABOPAY!*