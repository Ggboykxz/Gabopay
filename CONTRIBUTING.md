# Contribution Guidelines

Merci pour votre intérêt à contribuer à GABOPAY ! Ce document vous guide pour contribuer efficacement au projet.

---

## 🌍 Code de Conduite

En contribuant à GABOPAY, vous acceptez de respecter notre code de conduite:
- Être respectueux et inclusif
- Accepter les critiques constructives de manière professionnelle
- Se concentrer sur ce qui est meilleur pour la communauté

---

## 🚦 Comment Contribuer

### 1. Signaler des Bugs

Utilisez les [GitHub Issues](https://github.com/Ggboykxz/Gabopay/issues) pour signaler les bugs.

**Template de rapport de bug:**

```markdown
## Description
Description claire et concise du bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
Ce qui devrait se passer.

## Actual Behavior
Ce qui se passe réellement.

## Screenshots
Si applicable, captures d'écran.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Version: [e.g., 1.0.0]
```

### 2. Proposer des Améliorations

Utilisez les GitHub Issues pour proposer des features:
- Décrivez le problème que vous souhaitez résoudre
- Proposez une solution
- Incluez des exemples de code si pertinent

### 3. Soumettre des Pull Requests

1. **Fork** le projet
2. Créez une **branche** (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'feat: ajout de...'`)
4. **Push** sur votre fork (`git push origin feature/ma-feature`)
5. Ouvrez une **Pull Request**

---

## 📋 Standards de Code

### Python

- **Style:** Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Linting:** `ruff check apps/api`
- **Type Checking:** `mypy apps/api`
- **Docstrings:** Format Google

```python
def create_charge(amount: int, phone: str) -> dict:
    """Crée une nouvelle charge de paiement.

    Args:
        amount: Montant en XAF (entier)
        phone: Numéro de téléphone au format international

    Returns:
        dict: Charge créée avec son ID et statut

    Raises:
        ValueError: Si le montant est invalide
    """
```

### JavaScript / TypeScript

- **Style:** ESLint + Prettier
- **Naming:** camelCase pour variables, PascalCase pour composants
- **Types:** Always use TypeScript types

### Git

- **Commits:** Format conventional commits
  - `feat: description`
  - `fix: description`
  - `docs: description`
  - `chore: description`
- **Branches:** `feature/`, `fix/`, `docs/`

---

## 🔧 Setup Development

```bash
# Cloner le projet
git clone https://github.com/Ggboykxz/Gabopay.git
cd Gabopay

# Installer les dépendances
npm install
poetry install

# Configuration pre-commit (optionnel)
npm run lint  # Vérifier le code
poetry run ruff check  # Linter Python
```

---

## 📝 Processus de Review

1. Les maintainers review dans les 48-72h
2. Feedback constructif et suggestions
3. adjustments si nécessaire
4. Merge une fois approved

---

## 🏷️ Labels des Issues

| Label | Description |
|-------|-------------|
| `bug` | Bug report |
| `feature` | Nouvelle fonctionnalité |
| `enhancement` | Amélioration existante |
| `documentation` | Docs à améliorer |
| `good first issue` | Idéal pour les débutants |
| `priority:high` | Priorité élevée |
| `help wanted` | Besoin d'aide |

---

## 💬 Communication

- **Discord:** [Lien à venir]
- **Email:** team@gabopay.ga
- **Issues:** GitHub Issues

---

Merci de contribuer à GABOPAY! 🇬🇦