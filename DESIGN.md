# Design System: Orbyon Sport
## Inspiration principale : EA FC Mobile + Tonsser + culture football mobile

---

## 1. Visual Theme & Atmosphere

**Densité :** 6/10 — Contenu riche mais chaque écran a une hiérarchie claire.
**Variance :** 8/10 — Asymétrie, layering, profondeur. Pas symétrique.
**Motion :** 7/10 — Spring physics, card reveals, shimmer perpetuel sur les cartes premium.

L'atmosphère est celle d'un **stade le soir sous les projecteurs** : profond, chaud, énergique. Comme EA FC Mobile — pas un dashboard d'entreprise, pas une appli crypto. Un espace où le joueur se sent protagoniste. Lumières de stade, rayons de projecteurs, depths de champ, ambiance vestiaire premium.

La complexité technique est invisible. L'utilisateur voit : son nom en grand, sa carte, son score, son rang. Tout le reste est secondaire.

---

## 2. Color Palette

- **Stadium Black** (`#07080F`) — Surface principale. Presque noir, légèrement teinté bleu nuit.
- **Deep Navy** (`#0D1028`) — Fond secondaire. Bleu nuit profond — comme le ciel de stade.
- **Card Dark** (`#111428`) — Fond des cards. Légèrement surélevé du fond.
- **Card Raised** (`#181B35`) — Cards en relief, états hover, modals.
- **Pitch Green** (`rgba(0,180,80,0.08)`) — Teinte subtile pour les éléments liés au terrain.
- **Electric Green** (`#00D96F`) — Accent principal. CTAs, états actifs, badges positifs. Plus saturé que l'Electric Lime, plus vivant. C'est la couleur de la victoire — comme dans EA FC.
- **Lime Bright** (`#C8FF57`) — Variante lime pour les highlights et top performers.
- **Trophy Gold** (`#FFD700`) — Scores, Machine Score, trophées, rankings top 3. Brillant, chaud, désirable.
- **UCL Blue** (`#2979FF`) — Tags secondaires, certifications FBref, liens.
- **Royal Purple** (`#7B2FFF`) — Tier Legend uniquement. Rare, premium.
- **Cloud** (`#EEF0FF`) — Texte principal. Légèrement bleuté, jamais pur blanc.
- **Fog** (`#6B7592`) — Texte secondaire, labels, métadonnées.
- **Bench** (`#353860`) — Éléments inactifs, disabled.
- **Alert Red** (`#FF3B5C`) — Erreurs, cartons rouges. Jamais décoratif.

**Jamais :**
- `#000000` pur
- Vert néon hacker `#39ff6a` (trop terminal)
- Cyan froid `#00e5ff` (trop SaaS)
- Fond blanc ou light mode
- Dégradés multicolores génériques

---

## 3. Typography — Le point le plus important

L'erreur du prototype précédent : Outfit est trop "app" et pas assez "game". EA FC Mobile utilise une typographie condensed ultra-bold qui donne le sentiment d'importance.

### Polices

- **Display (titres héros, noms joueurs, scores) :** `Barlow Condensed` poids 800-900, ou `Bebas Neue` pour les très gros éléments. UPPERCASE obligatoire. Tracking -0.02em à -0.04em.  
  → "MARCUS FONTAINE", "78", "#11", "MON ÉQUIPE"
  
- **UI (labels, navigation, boutons) :** `Barlow` poids 600-700, pas condensed. Uppercase pour les labels.

- **Corps :** `Inter` (exception : le contexte gaming justifie Inter pour la lisibilité des paragraphes courts) ou `DM Sans`.

- **Chiffres/Stats :** `Barlow Condensed` 800 pour les grands chiffres (score, classement). `JetBrains Mono` pour les tableaux de stats détaillées.

### Hiérarchie EA FC Mobile

```
Score joueur (Machine Score) : Barlow Condensed 900, 4-5rem, Trophy Gold
Nom joueur (profil) :          Barlow Condensed 800, 2rem, Cloud, UPPERCASE
Attributs (TEC, PHY...) :      Barlow Condensed 700, 1.8rem chiffre / 0.65rem label
Navigation labels :             Barlow 700, 0.55rem, UPPERCASE
Corps text :                    DM Sans 400, 0.85rem
```

**Jamais :**
- `Outfit` seul pour les éléments premium (trop rond/app)
- `Inter` pour les gros titres (trop corporate)
- Minuscule pour les noms de joueurs sur les cards

---

## 4. Player Card — Spec complète EA FC Mobile style

La carte est le composant signature. Elle doit ressembler exactement aux cartes FUT — pas juste s'en inspirer.

### Structure (ratio 2:2.9)

```
┌─────────────────────────────┐
│ [Score] [POS]  [🇲🇶] [⚽]  │  ← Top left: score + position
│                              │
│                              │
│     [PHOTO JOUEUR]           │  ← Centre: photo plein format
│     (cutout fond)            │     55% de la hauteur totale
│                              │
│ ░░░░░░ gradient fade ░░░░░░ │
│                              │
│      MARCUS FONTAINE         │  ← Barlow Condensed 800 UPPER
│ ─────────────────────────── │  ← Divider teinté tier
│  74    79    76    82    71  │  ← Stats 3+3 grid
│ TEC   PHY   VIT   DEF   VIS │
└─────────────────────────────┘
```

### Tiers et backgrounds — EA FC style

| Tier | Score | Background | Border | Accent | Shadow |
|------|-------|-----------|--------|--------|--------|
| **Bronze** | 0-59 | `linear-gradient(160deg,#2a1a0a,#1a0f05)` | `rgba(180,100,30,0.5)` | `#CD7F32` | bronze glow |
| **Silver** | 60-74 | `linear-gradient(160deg,#1a1a22,#252530)` | `rgba(180,180,200,0.4)` | `#C8C8D8` | grey glow |
| **Gold** | 75-84 | `linear-gradient(160deg,#1a1a2e,#0f1e50)` | `rgba(255,200,50,0.6)` | `#FFD700` | gold glow |
| **Elite** | 85-94 | `linear-gradient(160deg,#1a0a2e,#300050)` | `rgba(150,50,255,0.6)` | `#B060FF` | purple glow |
| **Legend** | 95-100 | `linear-gradient(160deg,#1a0a0a,#400020)` | `rgba(255,60,100,0.7)` | `#FF3C64` | red-pink glow |

Shimmer holographique (animation CSS sur ::after) sur les tiers Gold, Elite, Legend.

### Photo joueur

- **Sans photo :** Zone avec icône caméra + "AJOUTE TA PHOTO" en Barlow Condensed
- **Avec photo :** object-fit cover, object-position top, dégradé fade vers le bas
- **Option IA :** Détourage de fond disponible (remove.bg ou modèle Python)
- **Upload flow :** Bottom sheet → caméra ou galerie → crop circulaire guidé → confirmation

### Ornements

Motif diagonal subtil en SVG repeating-linear-gradient dans le fond de la carte (comme les cartes EA FC qui ont une texture). Opacité 0.05.

---

## 5. Screens et composants clés EA FC Mobile style

### 5.1 Header joueur (style "fiche Ronaldo")

```
[CARD mini] [NOM EN GRAND BARLOW]    [COMPARAISON btn]
            [physique: taille/poids/pied]
            [drapeau + nationalité + catégorie]
─────────────────────────────────────────────────────
GÉN        RAPIDITÉ   TIRS    PASSES   DRIBBLES  DEF   PHY
[score]    [chiffre]  [chif]  [chif]   [chif]   [chif] [chif]
           Electric   Gold    Gold     Gold      Fog    Fog
           Green si best stat
```

### 5.2 Formation / Équipe type (style "Mon Équipe" EA FC)

Pitch vertical vert (`#0a2010`) avec lignes blanches à 10% d'opacité. Cards miniatures des joueurs positionnées selon la formation. Tap sur un joueur → ouvre sa fiche.

### 5.3 Écran principal / Home (style menu EA FC Mobile)

- Fond : stadium noir avec rayons de lumière violets/bleus en arrière-plan (SVG ou CSS radial-gradient)
- Élément central : trophy 3D ou logo Orbyon Sport grand format
- Cards événements : style EA FC (actualités, match of the week, challenge)
- Bottom nav avec 5 tabs

### 5.4 Navigation bottom bar

```css
background: rgba(7,8,15,0.96);
backdrop-filter: blur(24px);
border-top: 1px solid rgba(255,255,255,0.06);
height: 72px + safe-area;
```

Tab actif : Electric Green `#00D96F`, sous-ligne de 2px.
Bouton central "+" : pill background Electric Green, shadow `0 4px 24px rgba(0,217,111,0.4)`.

### 5.5 Stats row (style attributs EA FC)

Grande ligne horizontale avec 6 stats. Le chiffre principal en Barlow Condensed 700, très grand (1.6rem+). Label en petit en dessous. Color coding :
- ≥ 80 → Electric Green
- 60-79 → Trophy Gold  
- < 60 → Fog

### 5.6 Tabs de page (style Résumé/Attributs/Styles)

```css
.tab-bar { border-bottom: 1px solid rgba(255,255,255,0.08); }
.tab { Barlow 700, 0.75rem, uppercase, Fog par défaut }
.tab.active { 
  color: #00D96F; 
  border-bottom: 2px solid #00D96F;
  position: relative; bottom: -1px;
}
```

---

## 6. Backgrounds — L'effet stade

Chaque écran doit avoir une profondeur atmosphérique, pas un fond plat.

### Pattern principal

```css
background: 
  radial-gradient(ellipse 80% 60% at 50% 0%, rgba(41,121,255,0.08) 0%, transparent 60%),
  radial-gradient(ellipse 60% 40% at 80% 80%, rgba(123,47,255,0.06) 0%, transparent 50%),
  radial-gradient(ellipse 50% 30% at 20% 70%, rgba(0,217,111,0.04) 0%, transparent 50%),
  #07080F;
```

Donne l'effet "stade la nuit avec des projecteurs colorés" sans être excessif.

### Variante hero (home screen, profil)

```css
background:
  radial-gradient(ellipse 100% 50% at 50% -10%, rgba(255,215,0,0.06) 0%, transparent 50%),
  radial-gradient(ellipse 80% 60% at 20% 100%, rgba(41,121,255,0.1) 0%, transparent 60%),
  radial-gradient(ellipse 80% 60% at 80% 100%, rgba(123,47,255,0.08) 0%, transparent 60%),
  #07080F;
```

---

## 7. Buttons — Style EA FC

### Primary (Electric Green)
```css
background: linear-gradient(135deg, #00D96F, #00B55C);
color: #07080F;
font-family: 'Barlow', sans-serif;
font-weight: 800;
font-size: 0.9rem;
letter-spacing: 0.08em;
text-transform: uppercase;
border-radius: 100px;
padding: 14px 32px;
box-shadow: 0 4px 20px rgba(0,217,111,0.35);
/* Active : translateY(-1px) + brightness(1.1) */
```

### Gold (Trophy / Premium)
```css
background: linear-gradient(135deg, #FFD700, #FF9500);
color: #07080F;
/* Même forme pill */
```

### Secondary / Ghost
```css
background: transparent;
border: 1.5px solid rgba(255,255,255,0.15);
color: #EEF0FF;
```

---

## 8. Motion — Spring + Gaming

- **Cards révélées :** Entrée de bas + fade, stagger 60ms entre items
- **Machine Score counter :** Slot machine — chiffres qui défilent vers le haut
- **Card tier upgrade :** Flash blanc → nouvelle carte apparaît (comme pack opening)
- **Shimmer holographique cards Gold/Elite/Legend :** `::after` pseudo-element, animation linear-gradient qui traverse la carte horizontalement, 3s infini
- **Bottom sheet :** Spring `stiffness: 300, damping: 25`
- **Stats counter :** Comptage animé des chiffres au montage (0 → valeur réelle, 800ms)
- **Spring par défaut :** `stiffness: 280, damping: 22`
- **Hardware only :** `transform` + `opacity` uniquement

---

## 9. Anti-Patterns — Interdits Absolus

**Couleurs :**
- Fond blanc / light mode
- `#000000` pur
- Vert hacker `#39ff6a` / cyan terminal `#00e5ff`
- Violet IA générique (`#7C3AED`)
- Dégradés multicolores vert→cyan sur surfaces principales
- Glassmorphism fort `backdrop-filter: blur()` sur cards (OK pour la nav uniquement)

**Typographie :**
- `Outfit` seul pour les titres héros et les noms sur les cards
- Minuscules pour les noms de joueurs sur les cartes
- Texte < 14px sur mobile
- Trop de styles différents sur un même écran (max 2 familles)

**Layout :**
- Grilles de 3 cards égales horizontales
- Éléments qui se chevauchent sans intention
- `h-screen` → `min-h-[100dvh]` toujours
- Horizontal scroll non intentionnel sur mobile

**Composants :**
- Spinner circulaire générique
- Tooltips sur mobile
- Dropdowns natifs `<select>` pour les actions importantes
- Cards sans profondeur (flat + no border)

**Ambiance :**
- Dashboard analytics SaaS
- Interface hacker/terminal
- Crypto/Web3 dark
- App de gestion d'entreprise
- Chatbot IA générique

---

## 10. Design Tokens

```css
/* ── Surfaces ───────────────────────────── */
--bg:         #07080F;
--bg-navy:    #0D1028;
--card:       #111428;
--card-up:    #181B35;

/* ── Text ──────────────────────────────── */
--text:       #EEF0FF;
--text-muted: #6B7592;
--text-ghost: #353860;

/* ── Accents ────────────────────────────── */
--green:      #00D96F;   /* primary CTA, actif */
--lime:       #C8FF57;   /* top performers, highlight */
--gold:       #FFD700;   /* Machine Score, trophées */
--blue:       #2979FF;   /* FBref certifié, tags */
--purple:     #7B2FFF;   /* tier Elite */
--red:        #FF3B5C;   /* tier Legend, alertes */
--bronze:     #CD7F32;   /* tier Bronze */

/* ── Borders ────────────────────────────── */
--border:        rgba(255,255,255,0.07);
--border-green:  rgba(0,217,111,0.25);
--border-gold:   rgba(255,215,0,0.35);

/* ── Typography ─────────────────────────── */
--font-display: 'Barlow Condensed', 'Bebas Neue', sans-serif;
--font-ui:      'Barlow', 'DM Sans', sans-serif;
--font-body:    'DM Sans', system-ui, sans-serif;
--font-mono:    'JetBrains Mono', monospace;

/* ── Spacing ────────────────────────────── */
--space-xs: 4px;  --space-sm: 8px;   --space-md: 16px;
--space-lg: 24px; --space-xl: 40px;  --space-2xl: 64px;

/* ── Radii ──────────────────────────────── */
--radius-sm:   8px;
--radius-md:   14px;
--radius-lg:   20px;
--radius-xl:   28px;
--radius-pill: 100px;

/* ── Motion ─────────────────────────────── */
--spring-stiff: 280;
--spring-damp:  22;
--dur-fast:     150ms;
--dur-mid:      300ms;
--dur-slow:     600ms;

/* ── Tiers ──────────────────────────────── */
--tier-bronze-accent: #CD7F32;
--tier-silver-accent: #C8C8D8;
--tier-gold-accent:   #FFD700;
--tier-elite-accent:  #B060FF;
--tier-legend-accent: #FF3C64;
```

---

## 11. Fonts à charger (Google Fonts)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800;900&family=Barlow:wght@600;700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
```

`Bebas Neue` peut être ajouté pour les très grands displays si `Barlow Condensed` n'est pas assez condensé sur certains éléments.

---

## 12. Différence vs version précédente

| Avant | Après |
|-------|-------|
| Fond charbon `#0E0F18` plat | Fond navy `#07080F` avec rayons de stade |
| Electric Lime `#C8FF57` | Electric Green `#00D96F` + Gold `#FFD700` |
| Outfit pour tout | Barlow Condensed pour display, DM Sans pour corps |
| Cards simples | Cards avec shimmer holographique + 5 tiers (Bronze ajouté) |
| Style "dark analytics" | Style "EA FC Mobile gaming" |
| Bottom nav sobre | Bottom nav gaming avec glow sur le "+" |
| Stats petites | Stats très grandes color-codées (comme EA FC) |
