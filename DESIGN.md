# Design System: Orbyon Sport

## 1. Visual Theme & Atmosphere

**Densité:** 5/10 — "Daily App Balanced". Espacé, aéré, respirable. Pas de cockpit data analyst.  
**Variance:** 7/10 — Asymétrie dans les layouts, mais structure cohérente dans les composants.  
**Motion:** 7/10 — Spring physics sur les interactions sociales. Cards qui "pop". Pas de cinématique excessive.

L'atmosphère est celle d'un **vestiaire après une victoire** : chaud, vivant, communautaire. Pas un terminal de trading, pas un dashboard d'entreprise. Pense au feed Instagram de la page officielle d'une académie de foot — énergique, coloré, centré sur les visages et les moments.

Le dark mode n'est pas là pour paraître "tech". Il est là pour faire ressortir les Player Cards dorées, les scores et les highlights vidéo — comme un stade le soir. Chaud, pas froid. Charbon boisé, pas noir électronique.

**Ce qu'on évite absolument :** le look "hacker/IA/terminal" (fond noir + vert néon), les dégradés violet-cyan, les glassmorphism génériques, les cartes avec `backdrop-filter: blur`. C'est un réseau social sportif pour des ados, pas une interface de trading crypto.

---

## 2. Color Palette & Roles

- **Field Dark** (`#0E0F18`) — Surface principale de l'app. Charbon boisé, légèrement chaud. Jamais pur noir.
- **Card Surface** (`#17182A`) — Fond des cards, modals, bottom sheets. Légèrement plus clair que Field Dark.
- **Card Raised** (`#1E2035`) — Cards en relief, états hover, éléments actifs surélevés.
- **Grass Line** (`rgba(255,255,255,0.06)`) — Séparateurs, borders subtils. Jamais plus épais que 1px.
- **Electric Lime** (`#C8FF57`) — Accent principal et unique. CTAs primaires, score actif, états sélectionnés, badge VOTM. Vibrant mais lisible sur fond sombre. Saturation 100% intentionnelle — c'est la couleur de la victoire.
- **Match Gold** (`#FFD60A`) — Machine Score, Player Card highlights, achievements, badges "certifié". Brillant comme un trophée.
- **Cloud White** (`#F2F4FF`) — Texte principal. Légèrement bleuté, pas pur blanc — plus doux sur les yeux.
- **Fog** (`#7B8098`) — Texte secondaire, métadonnées, labels, timestamps.
- **Bench** (`#3D4060`) — Texte désactivé, placeholders, éléments inactifs.
- **Goal Red** (`#FF4757`) — Alertes, scores négatifs, erreurs. Jamais utilisé comme accent décoratif.
- **Sky Blue** (`#3D9AFF`) — Liens, tags secondaires, badges de niveau (FBref certifié). Ne pas utiliser comme accent principal.

**Jamais :** `#000000`, `#39ff6a` (vert neon hackers), `#00e5ff` (cyan terminal), violet (`#AA44FF`), gradients multicolores sur les surfaces principales.

---

## 3. Typography Rules

- **Display & Grandes Headlines :** `Outfit` — poids 800–900. Track `-0.04em`. La police qui ressemble à un maillot de foot, pas à une interface tech. Titles qui prennent toute la place quand nécessaire (Machine Score = 3rem bold).
- **Body & UI :** `Outfit` — poids 400–600. Leading `1.55`. Jamais plus de 60 caractères par ligne sur mobile.
- **Mono (scores, stats, timecodes) :** `JetBrains Mono` — utilisé uniquement pour les chiffres dans les classements, temps de jeu, stats agrégées. Donne du poids aux nombres sans paraître technique.
- **Hiérarchie par poids, pas par taille :** un h3 Outfit 700 est plus lisible qu'un h1 Outfit 300 + gros.

**Interdits :**
- `Inter` — trop corporate/SaaS
- `Geist` — trop dark mode tech
- `Roboto` — trop Android générique
- Grandes phrases en gradient-text — réservé uniquement aux titres de Player Card (un seul endroit dans l'app)
- Taille de corps < 14px sur mobile

---

## 4. Component Stylings

### Player Card (composant signature — style EA FC FUT)

L'élément central et le plus partageable de l'app. Inspiré directement des cartes EA FC Ultimate Team. **La photo réelle du joueur est obligatoire** — c'est ce qui rend la carte émotionnelle et partageable.

#### Dimensions et structure
```
Format : 220×320px (ratio 2:2.9 portrait) — exportable en PNG
Border-radius : 16px
Position des éléments (du haut vers le bas) :
  1. Top left : Score (Oswald 700, 2.4rem) + Position (0.7rem, uppercase)
  2. Top left suite : Drapeau pays (20×14px) + Badge club (20px)
  3. Centre : Photo joueur (occupe 55% de la hauteur de la carte)
  4. Bas photo : Dégradé fade vers la couleur du fond
  5. Nom joueur : Oswald 700, 1.05rem, uppercase, centré
  6. Séparateur 1px teinté selon le tier
  7. Stats grille 3×2 : Oswald 600 pour les chiffres, 0.52rem uppercase pour les labels
```

#### Tiers par Machine Score — palette et fond
| Tier | Score | Fond | Accent | Box-shadow |
|------|-------|------|--------|------------|
| **Silver** | 0-74 | `linear-gradient(160deg, #1a1a1a, #2d2d2d, #111)` | `rgba(180,180,200,0.4)` | `rgba(0,0,0,0.4)` |
| **Gold** | 75-84 | `linear-gradient(160deg, #1a1a2e, #16213e, #0f3460)` | `rgba(255,200,60,0.6)` | `rgba(255,180,30,0.25)` |
| **Elite** | 85-94 | `linear-gradient(160deg, #2d1515, #4a1010, #1a0505)` | `rgba(220,60,60,0.7)` | `rgba(255,60,60,0.3)` |
| **Legend** | 95-100 | `linear-gradient(160deg, #1a0d2e, #2d1a4a, #0d0d1a)` | `rgba(180,100,255,0.6)` | `rgba(160,80,255,0.35)` |

La carte se **met à jour visuellement** (animation flip) quand le joueur change de tier.

#### Ornements de coin
SVG paths aux 4 coins de la carte — même style que les cartes FUT. Couleur = accent du tier.

#### Photo joueur — import obligatoire
```
Flux :
1. Tap sur la zone photo (ou sur le bouton "+ Photo") → bottom sheet
2. Options : "Prendre une photo" (caméra) ou "Choisir dans la galerie"
3. Cropping interactif : cercle de sélection, zoom possible
4. Option IA : "Détourer le fond" (suppression background via API)
5. Photo sauvegardée → card régénérée et téléchargeable

Sans photo : zone placeholder avec icône caméra + "Ajouter ma photo"
Avec photo : objet-fit cover + dégradé fade vers le bas
```

#### Stats (6 dimensions du Machine Score)
```
TEC — Technique (touches, dribbles, précision passe)
PHY — Physique (duels, intensité, distance)
VIT — Vitesse (vitesse déplacement, transitions)
DEF — Défense (actions défensives, pressings)
VIS — Vision (passes clés, créativité)
IMP — Impact (buts, décisivité, moments clés)
```

Jamais de glow coloré (`box-shadow: 0 0 30px #couleur`). La profondeur vient du fond sombre et des ornements.

### Buttons

- **Primary (CTA Electric Lime) :** `background: #C8FF57`, texte `#0E0F18`, Outfit 800, border-radius 50px (pill), padding `14px 28px`. On active : `-2px translateY` + légère desaturation. Jamais de box-shadow outer glow.
- **Secondary :** `background: transparent`, border `1.5px solid rgba(255,255,255,0.15)`, texte Cloud White. Same pill shape. Hover : border Electric Lime.
- **Danger :** `background: rgba(255,71,87,0.12)`, border `1px solid rgba(255,71,87,0.3)`, texte Goal Red.
- **Ghost social (like, share) :** Icône uniquement, 44×44px touch target, background `rgba(255,255,255,0.05)` on hover.

### Feed Cards (posts, matchs, activité)

```
Background : Card Surface #17182A
Border : 1px solid rgba(255,255,255,0.06)
Border-radius : 18px
Padding : 16px
Shadow : 0 2px 12px rgba(0,0,0,0.3)
```

Pas d'effet glassmorphism. Pas de backdrop-filter. Les cards sont solides, pas floues.

### Bottom Navigation Bar

```
Height : 72px + safe-area-inset-bottom
Background : rgba(14,15,24,0.95) + backdrop-blur(20px)
Border-top : 1px solid rgba(255,255,255,0.06)
Icônes : 24px, couleur Fog par défaut, Electric Lime si actif
Labels : Outfit 600 0.6rem, uppercase, letter-spacing 0.07em
```

Le bouton central "+" est pill (`background: Electric Lime`, texte `#0E0F18`, height 52px, border-radius 100px, shadow `0 4px 20px rgba(200,255,87,0.35)`).

### Vote / Badges

```
Badge pill compact : padding 3px 10px, border-radius 100px
Fond : rgba(accent, 0.12)
Border : 1px solid rgba(accent, 0.25)
Text : Outfit 700, 0.62rem, uppercase, accent color
```

Les badges ne s'empilent pas — ils sont scrollables horizontalement.

### Inputs & Forms

```
Background : Card Raised #1E2035
Border : 1px solid rgba(255,255,255,0.1)
Border-radius : 14px
Focus : border Electric Lime 1.5px
Label : Outfit 600, 0.68rem, Fog, uppercase, margin-bottom 6px
Error : Goal Red, 0.72rem, sous l'input
```

Pas de floating labels (confusion UX pour les jeunes).

### Skeletal Loaders

Dimensions qui correspondent exactement au contenu attendu. Couleur `rgba(255,255,255,0.04)` → `rgba(255,255,255,0.08)`. Animation shimmer horizontal 1.5s ease-in-out infinite. Jamais de spinner circulaire générique.

### Empty States

Illustration minimaliste (style line art soccer) + titre Outfit 800 + phrase encourageante courte. CTA Electric Lime. Pas de "Aucun résultat trouvé" seul.

---

## 5. Layout Principles

- **Mobile-first absolu :** Tout est conçu pour 390px d'abord. L'app existe principalement sur téléphone.
- **Single column sur mobile :** Toute grille se replie en colonne unique < 768px. Aucune exception.
- **Bottom Sheet pattern :** Modals et actions contextuelles apparaissent par le bas (handle 36×4px centered), border-radius 28px top. Pas de modals centré verticalement sur mobile.
- **Pas de scroll horizontal accidentel :** Seuls les carrousels explicites (vote players, badges, classement tabs) scrollent horizontalement.
- **Safe areas :** `padding-bottom: env(safe-area-inset-bottom)` sur tout ce qui touche le bas de l'écran.
- **Grid uniquement via CSS Grid :** Jamais de calc() hacky pour les colonnes.
- **Spacing scale :** 4px base. Multiples de 4 : 8, 12, 16, 20, 24, 32, 40, 48, 64.
- **Max-width desktop :** Contenu centré à 480px max (comme une app mobile native dans le browser). Pas de layout "desktop wide" — l'app est mobile-first.

### Navigation principale (Bottom Nav)
5 onglets : Feed / Profil / + / Classements / Équipe. Le `+` central est le seul élément qui dépasse la bar. Sticky, always visible.

---

## 6. Motion & Interaction

- **Spring physics universel :** `stiffness: 280, damping: 22`. Sensation organique, jamais linéaire ou ease-in-out générique.
- **Card reveal (feed) :** Staggered cascade, délai `i * 60ms`, translateY(12px) → 0 + opacity 0 → 1. 
- **Player Card flip reveal :** rotateY(180deg) → 0, `transform-style: preserve-3d`, durée 600ms. Utilisé lors de la mise à jour du Machine Score.
- **Vote tap feedback :** Scale 0.9 → 1.05 → 1 sur 300ms. Tactile.
- **Machine Score counter :** Chiffres qui défilent vers le haut (slot machine style) quand le score est mis à jour.
- **Bottom sheet :** translateY(100%) → 0, spring damping 18. Backdrop fade-in simultané.
- **Bouton primary :** `-2px translateY` sur active + légère desaturation. 150ms spring.
- **Notification badge :** Pulse `scale(1) → scale(1.15) → scale(1)`, 2s infini.

**Règles GPU :**
- Uniquement `transform` et `opacity` en animation. Jamais `top/left/width/height`.
- `will-change: transform` uniquement sur les éléments fréquemment animés (Player Card, Bottom Sheet).
- Grain/noise en `position: fixed`, pointer-events: none, sur pseudo-élément — jamais sur des éléments scrollables.

---

## 7. Anti-Patterns — Interdits Absolus

**Couleurs :**
- `#000000` pur noir — utiliser Field Dark `#0E0F18`
- Vert néon hacker `#39ff6a` — remplacé par Electric Lime `#C8FF57`
- Cyan terminal `#00e5ff`
- Violet/mauve IA `#AA44FF`, `#7C3AED`
- Gradients multicolores (vert→cyan, violet→bleu)
- `box-shadow` outer glow coloré (`0 0 30px #couleur`)
- Glassmorphism `backdrop-filter: blur()` sur les cards principales

**Typographie :**
- `Inter` — interdit
- Serif fonts (`Times New Roman`, `Georgia`)
- Gradient text sur les titres principaux de l'app (uniquement Player Card)
- Texte < 14px sur mobile
- Uppercase sur tout — uniquement labels et badges

**Layout :**
- Grille de 3 cards égales horizontalement — utiliser scroll horizontal ou 1 colonne
- Modals centrés verticalement sur mobile — utiliser bottom sheets
- Éléments qui se chevauchent (`position: absolute` sur du contenu essentiel)
- `h-screen` — utiliser `min-h-[100dvh]`

**Contenu :**
- Emojis dans le texte de l'interface (icônes SVG ou emoji uniquement dans les badges utilisateurs)
- Noms génériques : "John Doe", "Joueur 1", "Équipe A"
- Chiffres inventés : "99.9% uptime", "12k joueurs actifs"
- Copywriting IA : "Révolutionnez", "Unleash", "Seamless", "Next-Gen", "Propulsez"
- "Scroll to explore", "Swipe down", flèches rebondissantes
- Sections fake "STATISTIQUES CLÉS" avec data inventée

**Composants :**
- Spinners circulaires génériques — skeletal loaders uniquement
- Tooltips sur mobile (inaccessibles au touch)
- Dropdowns natifs `<select>` pour les choix importants — bottom sheets toujours

**Ambiance générale :**
- Dashboard analytics SaaS
- Interface "hacker / terminal"
- Look crypto/web3
- Fintech sombre
- Chatbot / assistant IA
- Corporate enterprise B2B

---

## 8. Design Tokens (référence rapide)

```css
/* Surfaces */
--color-bg:          #0E0F18;
--color-card:        #17182A;
--color-card-raised: #1E2035;

/* Text */
--color-text:        #F2F4FF;
--color-text-muted:  #7B8098;
--color-text-ghost:  #3D4060;

/* Accents */
--color-lime:        #C8FF57;  /* accent principal */
--color-gold:        #FFD60A;  /* scores, achievements */
--color-red:         #FF4757;  /* alertes */
--color-blue:        #3D9AFF;  /* tags secondaires */

/* Borders */
--color-border:      rgba(255,255,255,0.06);
--color-border-lime: rgba(200,255,87,0.25);
--color-border-gold: rgba(255,214,10,0.25);

/* Typography */
--font-display: 'Outfit', sans-serif;
--font-mono:    'JetBrains Mono', monospace;

/* Spacing */
--space-xs:  4px;
--space-sm:  8px;
--space-md:  16px;
--space-lg:  24px;
--space-xl:  40px;

/* Radii */
--radius-sm:   10px;
--radius-md:   16px;
--radius-lg:   20px;
--radius-xl:   28px;  /* bottom sheets, large cards */
--radius-pill: 100px; /* buttons, badges */

/* Motion */
--spring-stiff:  280;
--spring-damp:   22;
--transition-fast: 150ms;
--transition-mid:  300ms;
```
