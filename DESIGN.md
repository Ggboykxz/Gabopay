# GABOPAY — DESIGN.md

> Système de design complet pour GABOPAY — Infrastructure de paiement gabonaise.
> Couvre : Dashboard Web (Next.js 15) + App Mobile (Expo React Native) + SDK Docs

---

## 🧭 PHILOSOPHIE DESIGN

**Identity statement :** GABOPAY est l'infrastructure financière sérieuse du Gabon.
Le design doit inspirer **confiance absolue**, **clarté des données**, et **vitesse d'action**.

**Trois mots qui gouvernent chaque décision design :**
1. **Précision** — chaque pixel a un rôle. Pas de décoration inutile.
2. **Autorité** — le produit doit avoir l'air plus pro que les banques locales.
3. **Local** — le vert du Gabon est l'âme du produit. Jamais générique.

**Anti-patterns à bannir :**
- ❌ Gradients purple/blue génériques façon "startup SaaS américaine"
- ❌ Illustrations plates et émojis dans les états vides
- ❌ Animations lentes ou décoratives (tout mouvement = information)
- ❌ Texte en FCFA avec décimales (les montants sont des entiers)
- ❌ Boutons arrondis façon bulle (border-radius max = 8px sur desktop)

---

## 🎨 COLOR SYSTEM

### Couleurs primitives (tokens de base)

```ts
// packages/shared/tokens/colors.ts

export const primitive = {
  // Verts Gabon — couleur identitaire
  green: {
    50:  '#e6f7ef',
    100: '#c3ead8',
    200: '#8fd5b2',
    300: '#5abf8c',
    400: '#2aaa6a',
    500: '#009e60', // ← PRIMARY — vert drapeau Gabon
    600: '#007d4d',
    700: '#005c39',
    800: '#003b24',
    900: '#001a10',
  },

  // Neutres — base du dashboard
  slate: {
    0:   '#ffffff',
    50:  '#f8f9fa',
    100: '#f1f3f5',
    200: '#e9ecef',
    300: '#dee2e6',
    400: '#ced4da',
    500: '#adb5bd',
    600: '#868e96',
    700: '#495057',
    800: '#343a40',
    900: '#212529',
    950: '#141618',
    1000:'#0a0b0c', // fond dark le plus profond
  },

  // Jaune Gabon — accent secondaire (alertes, badges premium)
  yellow: {
    400: '#ffd43b',
    500: '#fcc419',
    600: '#f59f00',
  },

  // Bleu Gabon — informations, liens
  blue: {
    400: '#4dabf7',
    500: '#339af0',
    600: '#228be6',
  },

  // Statuts
  red: {
    400: '#ff6b6b',
    500: '#fa5252',
    600: '#f03e3e',
  },
  orange: {
    400: '#ffa94d',
    500: '#fd7e14',
  },
} as const;
```

### Tokens sémantiques

```ts
// packages/shared/tokens/semantic.ts

export const semantic = {
  // === DARK THEME (dashboard principal) ===
  dark: {
    // Backgrounds
    bg: {
      base:     '#0a0b0c', // fond app principal
      surface:  '#111214', // cards, modals, panels
      elevated: '#18191c', // hover states, dropdowns
      overlay:  '#1e2023', // sidebars, popups
    },

    // Bordures
    border: {
      subtle:  '#1e2023', // séparateurs discrets
      default: '#2a2d31', // bordures de cards
      strong:  '#3a3e44', // bordures actives, focus
    },

    // Texte
    text: {
      primary:   '#f1f3f5', // titres, montants
      secondary: '#868e96', // labels, métadonnées
      tertiary:  '#495057', // placeholders, disabled
      inverse:   '#0a0b0c', // texte sur fond clair
    },

    // Accent principal (vert Gabon)
    brand: {
      default:  '#009e60',
      hover:    '#007d4d',
      active:   '#005c39',
      subtle:   '#003b24', // bg de badges brand
      on:       '#e6f7ef', // texte sur fond brand
    },

    // Statuts
    status: {
      success:       '#009e60',
      successBg:     '#001a10',
      successBorder: '#003b24',

      error:         '#fa5252',
      errorBg:       '#1a0505',
      errorBorder:   '#3b1010',

      warning:       '#fcc419',
      warningBg:     '#1a1400',
      warningBorder: '#3b2e00',

      pending:       '#339af0',
      pendingBg:     '#050f1a',
      pendingBorder: '#0e2d4a',

      processing:    '#fd7e14',
      processingBg:  '#1a0a00',
      processingBorder: '#3b1f00',
    },
  },

  // === LIGHT THEME (docs, portail public) ===
  light: {
    bg: {
      base:     '#ffffff',
      surface:  '#f8f9fa',
      elevated: '#f1f3f5',
      overlay:  '#e9ecef',
    },
    border: {
      subtle:  '#f1f3f5',
      default: '#dee2e6',
      strong:  '#ced4da',
    },
    text: {
      primary:   '#141618',
      secondary: '#495057',
      tertiary:  '#868e96',
      inverse:   '#ffffff',
    },
    brand: {
      default:  '#009e60',
      hover:    '#007d4d',
      active:   '#005c39',
      subtle:   '#e6f7ef',
      on:       '#003b24',
    },
  },
} as const;
```

### Variables CSS (Dashboard Next.js)

```css
/* apps/dashboard/styles/tokens.css */

:root {
  /* Brand */
  --color-brand:        #009e60;
  --color-brand-hover:  #007d4d;
  --color-brand-subtle: #003b24;

  /* Backgrounds */
  --bg-base:     #0a0b0c;
  --bg-surface:  #111214;
  --bg-elevated: #18191c;
  --bg-overlay:  #1e2023;

  /* Borders */
  --border-subtle:  #1e2023;
  --border-default: #2a2d31;
  --border-strong:  #3a3e44;

  /* Text */
  --text-primary:   #f1f3f5;
  --text-secondary: #868e96;
  --text-tertiary:  #495057;

  /* Status */
  --status-success: #009e60;
  --status-error:   #fa5252;
  --status-warning: #fcc419;
  --status-pending: #339af0;

  /* Spacing */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.6);
  --shadow-brand: 0 0 0 3px rgba(0,158,96,0.25);
}
```

### Tokens NativeWind (App mobile Expo)

```ts
// apps/mobile/theme/colors.ts — utilisé dans tailwind.config.js

module.exports = {
  theme: {
    extend: {
      colors: {
        brand:   { DEFAULT: '#009e60', hover: '#007d4d', subtle: '#003b24' },
        bg:      { base: '#0a0b0c', surface: '#111214', elevated: '#18191c' },
        border:  { subtle: '#1e2023', default: '#2a2d31', strong: '#3a3e44' },
        text:    { primary: '#f1f3f5', secondary: '#868e96', muted: '#495057' },
        success: '#009e60',
        error:   '#fa5252',
        warning: '#fcc419',
        pending: '#339af0',
      },
      fontFamily: {
        mono:    ['GeistMono', 'monospace'],
        display: ['InterDisplay', 'Inter', 'sans-serif'],
        body:    ['Inter', 'sans-serif'],
      },
    },
  },
};
```

---

## 🔤 TYPOGRAPHIE

### Familles

| Rôle | Famille | Usage |
|---|---|---|
| **Display** | Inter Display (700, 600) | Titres de pages, headings H1-H2 |
| **Body** | Inter (400, 500) | Texte courant, labels, paragraphes |
| **Mono** | Geist Mono (400, 500) | Montants FCFA, API keys, codes, TX IDs |
| **Data** | Geist Mono (600) | Soldes, gros chiffres dashboard |

### Échelle typographique

```ts
// packages/shared/tokens/typography.ts

export const typography = {
  // Tailles
  size: {
    xs:   '11px', // métadonnées, timestamps
    sm:   '12px', // badges, tags
    base: '13px', // texte courant dashboard
    md:   '14px', // boutons, inputs, labels
    lg:   '16px', // sous-titres
    xl:   '18px', // titres de section
    '2xl':'22px', // titres de page
    '3xl':'28px', // montants principaux
    '4xl':'36px', // solde total dashboard
    '5xl':'48px', // KPI hero
  },

  // Line heights
  leading: {
    tight:  1.2,
    normal: 1.5,
    relaxed: 1.7,
  },

  // Letter spacing
  tracking: {
    tight:  '-0.02em',
    normal: '0em',
    wide:   '0.05em',
    widest: '0.12em', // pour les montants mono
  },

  // Weights
  weight: {
    regular:  400,
    medium:   500,
    semibold: 600,
    bold:     700,
  },
} as const;
```

### Règles de formatage des montants FCFA

```ts
// packages/shared/utils/currency.ts

// RÈGLE : jamais de décimales en FCFA
// RÈGLE : espace comme séparateur de milliers (standard français)
// RÈGLE : toujours afficher "FCFA" après le montant

export function formatXAF(amountInCentimes: number): string {
  const amount = Math.round(amountInCentimes / 100);
  return new Intl.NumberFormat('fr-GA', {
    style: 'currency',
    currency: 'XAF',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
  // → "10 000 FCFA"
}

// Dans les composants : toujours font-mono pour les montants
// <span className="font-mono text-3xl font-semibold tracking-wide">
//   {formatXAF(transaction.amount)}
// </span>
```

---

## 📐 SPACING & LAYOUT

### Grille Dashboard (Next.js)

```
Sidebar :  240px fixe (collapsed: 64px)
Content :  flex-1, max-width: 1280px, padding: 24px
Header  :  64px fixe, sticky top
Gap     :  24px entre cards
```

### Grille Mobile (Expo)

```
Padding horizontal : 16px (sm) / 20px (md)
Safe area          : toujours respectée
Card padding       : 16px interne
Gap entre éléments : 12px (liste) / 24px (sections)
Bottom nav height  : 64px + safe area
```

### Composants — hauteurs standards

| Composant | Height | Note |
|---|---|---|
| Input | 40px | Desktop |
| Input | 48px | Mobile |
| Button sm | 32px | — |
| Button md | 40px | Default |
| Button lg | 48px | CTA mobile |
| Table row | 48px | — |
| Nav item | 40px | Sidebar |
| Badge | 22px | — |

---

## 🧩 COMPOSANTS

### 1. TransactionBadge — Badge statut transaction

```tsx
// packages/shared/components/TransactionBadge.tsx

type Status = 'succeeded' | 'failed' | 'pending' | 'processing' | 'refunded';

const config: Record<Status, { label: string; class: string }> = {
  succeeded:  { label: 'Succès',      class: 'bg-[#001a10] text-[#009e60] border-[#003b24]' },
  failed:     { label: 'Échoué',      class: 'bg-[#1a0505] text-[#fa5252] border-[#3b1010]' },
  pending:    { label: 'En attente',  class: 'bg-[#050f1a] text-[#339af0] border-[#0e2d4a]' },
  processing: { label: 'En cours',   class: 'bg-[#1a0a00] text-[#fd7e14] border-[#3b1f00]' },
  refunded:   { label: 'Remboursé',  class: 'bg-[#0a0a1a] text-[#868e96] border-[#2a2d31]' },
};

export function TransactionBadge({ status }: { status: Status }) {
  const { label, class: cls } = config[status];
  return (
    <span className={`
      inline-flex items-center gap-1.5 px-2 py-0.5
      text-[11px] font-medium tracking-wide uppercase
      border rounded-[4px] font-mono
      ${cls}
    `}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {label}
    </span>
  );
}
```

### 2. ProviderBadge — Badge provider paiement

```tsx
// Airtel Money = rouge #E4002B + blanc
// Moov Money  = vert/bleu #00A79D + blanc
// Card        = ardoise #3a3e44 + blanc

const providers = {
  airtel_money: {
    label: 'Airtel Money',
    bg: '#1a0005',
    text: '#ff4d6a',
    border: '#3b000f',
    icon: '📡', // remplacer par SVG Airtel
  },
  moov_money: {
    label: 'Moov Money',
    bg: '#001a1a',
    text: '#00d4c8',
    border: '#003b3b',
    icon: '📶',
  },
  card: {
    label: 'Carte',
    bg: '#111214',
    text: '#868e96',
    border: '#2a2d31',
    icon: '💳',
  },
};
```

### 3. AmountDisplay — Affichage montant principal

```tsx
// Règle : montants toujours en Geist Mono, jamais de décimales

type Size = 'sm' | 'md' | 'lg' | 'xl';

const sizeMap = {
  sm: 'text-base font-medium',
  md: 'text-xl font-semibold',
  lg: 'text-3xl font-semibold',
  xl: 'text-4xl font-bold',
};

export function AmountDisplay({
  amount,        // en centimes FCFA
  size = 'md',
  negative = false,
}: {
  amount: number;
  size?: Size;
  negative?: boolean;
}) {
  const formatted = formatXAF(amount);
  return (
    <span className={`
      font-mono tracking-wide
      ${sizeMap[size]}
      ${negative ? 'text-red-400' : 'text-[#f1f3f5]'}
    `}>
      {negative ? '−' : ''}{formatted}
    </span>
  );
}
```

### 4. MetricCard — Card KPI Dashboard

```tsx
// Carte de métrique principale (volume, transactions, taux succès...)

interface MetricCardProps {
  label: string;
  value: string | number;
  isCurrency?: boolean;
  change?: number;    // en % vs période précédente
  icon?: React.ReactNode;
}

// Structure visuelle :
// ┌────────────────────────────────┐
// │ [icon]  Label          +12.5% │
// │                               │
// │  10 500 000 FCFA              │
// │                               │
// │ vs hier  ─────────────────    │
// └────────────────────────────────┘

// Classes :
// Card : bg-[#111214] border border-[#2a2d31] rounded-lg p-6
// Label : text-[13px] text-[#868e96] font-medium
// Value : font-mono text-4xl font-bold text-[#f1f3f5] mt-2
// Change positive : text-[#009e60] bg-[#001a10] px-2 py-0.5 rounded text-xs
// Change negative : text-[#fa5252] bg-[#1a0505] px-2 py-0.5 rounded text-xs
```

### 5. DataTable — Table de transactions

```
Colonnes standard pour /dashboard/transactions :

ID          | font-mono text-xs text-[#868e96]  | ch_01J7XXX...  (tronqué 12 chars)
Date        | text-[13px] text-[#868e96]        | 08 mai 2026, 14:32
Montant     | font-mono font-semibold text-right | 10 000 FCA
Provider    | ProviderBadge                      | Airtel Money
Téléphone   | font-mono text-sm                  | +241 77 00 00 00
Statut      | TransactionBadge                   | Succès / Échoué
Actions     | IconButton                         | Voir / Rembourser

Header : text-[11px] uppercase tracking-widest text-[#495057] font-medium
Row hover : bg-[#18191c] transition-colors duration-100
Row border-b : border-[#1e2023]
```

### 6. APIKeyCard — Carte clé API

```
Structure :
┌─────────────────────────────────────────────────┐
│ ● LIVE    ma-clé-production          [Copier]   │
│ gp_live_sk_••••••••••••••••••XK9m               │
│                                                  │
│ Créée le 01 mai 2026 · Dernière utilisation : ✓ │
│ [Révoquer]                                [Voir]│
└─────────────────────────────────────────────────┘

- Fond : bg-[#111214] border border-[#2a2d31]
- Mode LIVE : badge vert #009e60
- Mode TEST : badge jaune #fcc419
- Key masquée : font-mono text-sm, afficher seulement préfixe + 4 derniers chars
- Bouton Copier : icône + toast "Copié !" 2s
```

### 7. WebhookLogRow — Ligne de log webhook

```
[200 OK] [2026-05-08 14:32:01] charge.succeeded → https://api.ecanda.ga/webhook
                                [Réessayer]  [Voir payload]

Status 2xx : text-[#009e60] bg-[#001a10]
Status 4xx : text-[#fcc419] bg-[#1a1400]
Status 5xx : text-[#fa5252] bg-[#1a0505]
Timeout    : text-[#868e96] bg-[#111214]
```

---

## 📱 COMPOSANTS MOBILE (Expo React Native)

### BalanceCard — Carte de solde principal

```tsx
// Composant hero de l'app mobile marchands

// ┌─────────────────────────────────┐
// │  GABOPAY                  [⚙]  │
// │                                 │
// │  Solde disponible               │
// │  125 000 FCA                    │
// │                                 │
// │  En attente : 15 000 FCA        │
// │                                 │
// │  [Retirer]     [Partager QR]    │
// └─────────────────────────────────┘

// Styles NativeWind :
// Container : bg-[#111214] rounded-xl p-5 mx-4 border border-[#2a2d31]
// Label     : text-text-secondary text-xs font-medium tracking-widest uppercase
// Amount    : text-text-primary text-4xl font-bold font-mono mt-1
// Pending   : text-text-secondary text-sm font-mono mt-3
// Buttons   : flex-row gap-3 mt-5
```

### TransactionRow — Ligne transaction mobile

```tsx
// ┌─────────────────────────────────────┐
// │  [A]  Airtel Money    +10 000 FCA   │
// │       +241 77 00 00   08 mai 14:32  │
// └─────────────────────────────────────┘

// Avatar provider : cercle 40x40, initiale ou logo
// Airtel : bg rouge foncé, initiale "A" rouge clair
// Moov   : bg teal foncé, initiale "M" teal clair
// Card   : bg slate, icône carte

// Montant positif (reçu)  : text-[#009e60] font-mono font-semibold
// Montant négatif (payout): text-[#fa5252] font-mono font-semibold
```

### QRPaymentSheet — Bottom sheet QR

```tsx
// Bottom sheet pour paiement en caisse via QR code

// ┌─────────────────────────────────┐
// │          ▬▬▬ (handle)          │
// │                                 │
// │  Montant                        │
// │  [    5 000        ] FCA        │
// │                                 │
// │  ┌───────────────────────────┐  │
// │  │  ████  ██  ████           │  │
// │  │  ██    ██  ██             │  │
// │  │  ████  ██  ████           │  │  ← QR code généré
// │  └───────────────────────────┘  │
// │                                 │
// │  ch_01J7GABOPAY123...           │
// │  Expire dans 04:59              │
// │                                 │
// │  [Annuler]                      │
// └─────────────────────────────────┘

// Handle : w-10 h-1 bg-[#2a2d31] rounded-full mx-auto mb-6
// Input montant : text-center text-4xl font-mono text-[#f1f3f5]
// QR : fond blanc (obligatoire pour scan), padding 16px, border-radius 8px
// Timer : text-[#fcc419] font-mono text-sm
```

---

## ✨ ANIMATIONS & TRANSITIONS

### Règles générales

```ts
// PRINCIPE : chaque animation transmet une information précise.
// Aucune animation purement décorative.

const motion = {
  // Entrée de page
  pageEnter: {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.2, ease: 'easeOut' },
  },

  // Entrée de liste (stagger)
  listItem: (index: number) => ({
    initial: { opacity: 0, x: -4 },
    animate: { opacity: 1, x: 0 },
    transition: { duration: 0.15, delay: index * 0.03 },
  }),

  // Slide-in de modal / bottom sheet
  modal: {
    initial: { opacity: 0, scale: 0.97 },
    animate: { opacity: 1, scale: 1 },
    transition: { duration: 0.15, ease: [0.16, 1, 0.3, 1] },
  },

  // Bottom sheet mobile
  sheet: {
    initial: { translateY: '100%' },
    animate: { translateY: '0%' },
    transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] },
  },

  // Transition statut transaction (PENDING → SUCCESS)
  statusChange: {
    duration: 0.3,
    ease: 'easeInOut',
  },
} as const;
```

### Micro-interactions clés

```
Bouton [Copier API Key]  → flash vert 200ms + checkmark 2s
Charge SUCCESS           → badge pulse 1x (scale 1→1.05→1) + bg flash vert
Charge FAILED            → shake horizontal 3px × 2 + bg flash rouge
Payout créé              → bottom toast slide-up + icône argent
Connexion dashboard      → skeleton → contenu avec fade 200ms
Rechargement table       → ligne spinner + opacité 0.4 pendant fetch
```

---

## 🔡 ICONOGRAPHIE

### Librairie : Lucide React (dashboard) + Lucide React Native (mobile)

```ts
// Mapping icônes — GABOPAY

import {
  // Navigation
  LayoutDashboard,  // Dashboard
  ArrowLeftRight,   // Transactions
  ArrowDownToLine,  // Payouts
  Code2,            // Développeurs / API
  Webhook,          // Webhooks
  Settings,         // Paramètres
  Users,            // Équipe
  FileText,         // Rapports

  // Actions
  Copy,             // Copier (API keys, TX ID)
  RotateCcw,        // Remboursement / Retry
  Eye, EyeOff,      // Afficher/masquer clé
  Plus,             // Créer nouveau
  Trash2,           // Révoquer
  Download,         // Export
  QrCode,           // QR payment
  Send,             // Payout

  // Statuts
  CheckCircle2,     // Succeeded
  XCircle,          // Failed
  Clock,            // Pending
  Loader2,          // Processing (avec animation spin)
  RefreshCw,        // Refunded

  // Providers (pas dans Lucide — utiliser SVG custom)
  // Airtel Money → /assets/icons/airtel.svg
  // Moov Money   → /assets/icons/moov.svg

  // Alertes
  AlertTriangle,    // Warning
  Info,             // Info
  ShieldCheck,      // Sécurité / Webhook secret
  Key,              // API Key
  Globe,            // URL webhook
  Zap,              // Mode live (actif)
  TestTube2,        // Mode test
} from 'lucide-react';

// Tailles standards
// Sidebar nav : 18px
// Dans bouton  : 16px
// Badge/statut : 14px
// Hero / empty state : 32px
```

---

## 📊 DATA VISUALIZATION

### Graphique volume (Recharts — Dashboard)

```tsx
// Palette de couleurs pour les graphiques

const chartColors = {
  primary:    '#009e60', // ligne/barre principale (volume total)
  secondary:  '#339af0', // comparaison (période précédente)
  airtel:     '#ff4d6a', // breakdown par provider
  moov:       '#00d4c8',
  card:       '#868e96',

  grid:       '#1e2023', // lignes de grille
  axis:       '#495057', // labels d'axe
  tooltip: {
    bg:     '#18191c',
    border: '#2a2d31',
    text:   '#f1f3f5',
  },
};

// Graphiques utilisés :
// /dashboard → AreaChart (volume 30 jours) + BarChart (par provider)
// /dashboard/transactions → pas de graphique (table pure)
// /dashboard/payouts → LineChart (évolution solde)
// Métriques rapides → SparkLine inline (mini 80×32px)
```

---

## 🔒 ÉTATS SPÉCIAUX

### États vides (Empty States)

```
Pas de transactions :
  Icône : ArrowLeftRight (32px, text-[#495057])
  Titre : "Aucune transaction"  (text-[#868e96])
  Body  : "Les transactions de vos clients apparaîtront ici."
  CTA   : "Voir la documentation" → link docs

Pas d'API key :
  Icône : Key (32px)
  Titre : "Aucune clé API"
  CTA   : Bouton "Créer une clé" (brand)

Mode TEST actif (bannière top) :
  Fond  : #1a1400 (jaune foncé)
  Texte : "Mode TEST — aucun vrai argent ne circule"  text-[#fcc419]
  Icône : TestTube2
  Position : sticky sous le header, full-width
```

### États de chargement (Skeleton)

```tsx
// Skeleton = bg-[#18191c] animate-pulse rounded

// MetricCard skeleton : h-24 w-full
// TableRow skeleton   : h-12 w-full × 8
// Montant skeleton    : h-10 w-40 (inline)
// Badge skeleton      : h-5 w-20
```

### États d'erreur

```
Erreur réseau :
  Toast rouge slide-up depuis le bas
  "Erreur de connexion — réessayer ?"
  Bouton [Réessayer] inline dans le toast

Erreur provider (Airtel down) :
  Badge PROVIDER_ERROR dans la transaction
  Tooltip : message d'erreur exact de l'API provider

Erreur 429 (rate limit) :
  Banner orange : "Limite de taux atteinte — upgrade votre plan"
```

---

## 🖨️ DESIGN TOKENS — FICHIER COMPLET (à copier dans le projet)

```ts
// packages/shared/tokens/index.ts
// Source de vérité unique — importer depuis ici partout

export const tokens = {
  color: {
    brand:   '#009e60',
    bg: {
      base:     '#0a0b0c',
      surface:  '#111214',
      elevated: '#18191c',
    },
    border: {
      subtle:  '#1e2023',
      default: '#2a2d31',
      strong:  '#3a3e44',
    },
    text: {
      primary:   '#f1f3f5',
      secondary: '#868e96',
      muted:     '#495057',
    },
    status: {
      success: '#009e60',
      error:   '#fa5252',
      warning: '#fcc419',
      pending: '#339af0',
      process: '#fd7e14',
    },
  },

  font: {
    mono:    'GeistMono, monospace',
    display: 'InterDisplay, Inter, sans-serif',
    body:    'Inter, sans-serif',
  },

  size: {
    xs: 11, sm: 12, base: 13, md: 14,
    lg: 16, xl: 18, '2xl': 22, '3xl': 28,
    '4xl': 36, '5xl': 48,
  },

  space: {
    1: 4,  2: 8,  3: 12, 4: 16,
    5: 20, 6: 24, 8: 32, 10: 40,
    12: 48, 16: 64,
  },

  radius: {
    sm: 4, md: 6, lg: 8, xl: 12, full: 9999,
  },

  shadow: {
    sm: '0 1px 2px rgba(0,0,0,0.4)',
    md: '0 4px 12px rgba(0,0,0,0.5)',
    lg: '0 8px 32px rgba(0,0,0,0.6)',
    brand: '0 0 0 3px rgba(0,158,96,0.25)',
  },

  zIndex: {
    base:    0,
    raised:  10,
    modal:   100,
    toast:   200,
    tooltip: 300,
  },
} as const;

export type Tokens = typeof tokens;
```

---

## 📋 CHECKLIST DESIGN — avant chaque commit

Avant de commiter un composant, vérifier :

- [ ] Montants en font-mono, aucune décimale sur les FCA
- [ ] Couleur brand uniquement `#009e60` (jamais approximée)
- [ ] Fond de card `#111214`, jamais `#000` ou `#1a1a1a` approximatif
- [ ] Tous les statuts utilisent TransactionBadge (pas de inline styles)
- [ ] États vide + loading + erreur implémentés
- [ ] Mode TEST : bannière jaune visible si `mode === 'test'`
- [ ] Responsive : sidebar collapsible sur < 1024px
- [ ] Mobile : SafeAreaView respectée, tap targets min 44×44px
- [ ] Animations : max 300ms, aucune animation loop infinie non stoppable
- [ ] Accessibilité : aria-label sur tous les IconButton

---

*GABOPAY Design System v1.0 — Construit à Libreville, Gabon 🇬🇦*
*Dernière mise à jour : Mai 2026*