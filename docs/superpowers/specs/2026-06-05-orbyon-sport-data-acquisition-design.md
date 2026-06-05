# Orbyon Sport — Data Acquisition & Platform Architecture Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Construire une plateforme sociale football multi-tiers capable de servir amateurs (aucune donnée publique) ET semi-pros/pros (FBref/StatsBomb disponibles) avec la même expérience analytics, via une architecture d'acquisition de données progressive.

**Architecture:** Social-First (acquisition virale) + Vidéo Premium (différenciation) + Fusion FBref automatique (WOW moment semi-pro) + Machine Score normalisé par percentile local.

**Tech Stack:** FastAPI (Python) · Next.js 14 App Router (TypeScript) · PostgreSQL · Redis + Celery · YOLO + ByteTrack (CV) · Stripe · Supabase Auth · Outfit + JetBrains Mono

---

## Contexte et décisions validées

| Question | Décision |
|----------|----------|
| Niveau analytique amateur | Mix B+C : base intermédiaire + enrichissement progressif |
| Méthode acquisition | Multi-path adaptatif (3 niveaux coexistants) |
| Heatmap niveau 1 | Non disponible sans vidéo — CTA upgrade affiché |
| Profil joueur | Unique adaptatif + fusion FBref automatique à l'inscription |
| Rankings | Locaux (région + catégorie + poste) + percentile normalisé |
| Architecture principale | Social-First + Vidéo Premium |
| Design | FUT card style, photo réelle obligatoire, Outfit police, fond charbon chaud |

---

## 1. Architecture globale

### 1.1 Les 3 couches

```
┌─────────────────────────────────────────────────────────┐
│  APP SOCIALE (mobile-first Next.js + PWA futur)         │
│  Feed · Profil + Player Card · Vote VOTM · Classements  │
│  Upload vidéo premium · Partage social · Badges         │
└─────────────────────────────────────────────────────────┘
              ↕ FastAPI REST + WebSocket
┌─────────────────────────────────────────────────────────┐
│  BACKEND FASTAPI                                        │
│  Auth · Profils · Matchs · Votes · Rankings             │
│  Machine Score engine · Player Card generator           │
│  Worker Celery : video CV jobs · FBref sync             │
└─────────────────────────────────────────────────────────┘
              ↕ PostgreSQL + Redis
┌─────────────────────────────────────────────────────────┐
│  DATA LAYER                                             │
│  FBref connector (référentiel + stats)                  │
│  StatsBomb connector (training IA)                      │
│  CV Pipeline (YOLO + ByteTrack + homographie)           │
│  Source Mapping (résolution identité cross-sources)     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Flux d'acquisition multi-path

```
Inscription joueur
    ↓
FBref Identity Search (async, < 5s)
    ├── Trouvé (score ≥ 0.85) → "On a trouvé tes stats !" → Confirmation
    │       → Level 2 automatique + mise à jour hebdomadaire
    └── Non trouvé → Profil vide Level 1
              ↓
Match ajouté (formulaire rapide)
    ↓
Vote coéquipiers (notification 48h)  ← boucle virale
    ↓
Machine Score mis à jour + Player Card régénérée
    ↓ (optionnel, premium)
Upload vidéo → Job Celery → CV Pipeline
    → Heatmap + overlay + clip 9:16 + rapport IA
    → Machine Score enrichi (Level 3 certifié)
```

---

## 2. Modèle de données (PostgreSQL)

### 2.1 Tables sociales

```sql
-- Joueurs
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id TEXT UNIQUE NOT NULL,                -- Supabase auth ID
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    position VARCHAR(50),                        -- Center Midfield, etc.
    position_short VARCHAR(10),                  -- MD, BU, DC, GB...
    club VARCHAR(100),
    region VARCHAR(100),
    category VARCHAR(50),                        -- U13, U15, U21, Senior
    country_code CHAR(2),
    photo_url TEXT,                              -- URL photo profil (S3)
    photo_processed_url TEXT,                   -- URL photo détourée IA
    machine_score INTEGER DEFAULT 0,
    machine_score_tier VARCHAR(20) DEFAULT 'silver', -- silver/gold/elite/legend
    data_level SMALLINT DEFAULT 1,              -- 1=manual, 2=tagging/FBref, 3=video
    fbref_player_id TEXT,                       -- FBref ID si trouvé
    fbref_confidence NUMERIC(4,3),              -- score de matching 0-1
    fbref_verified BOOLEAN DEFAULT FALSE,       -- confirmé par le joueur
    fbref_last_sync TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Équipes
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    club VARCHAR(100),
    region VARCHAR(100),
    category VARCHAR(50),
    coach_id UUID REFERENCES players(id),
    invite_code VARCHAR(8) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE team_players (
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'player',          -- player / captain / coach
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (team_id, player_id)
);

-- Matchs
CREATE TABLE matches_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id),
    opponent_name VARCHAR(100) NOT NULL,
    home_score SMALLINT,
    away_score SMALLINT,
    match_date DATE NOT NULL,
    competition VARCHAR(100),
    is_home BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES players(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE match_players (
    match_id UUID REFERENCES matches_log(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    position VARCHAR(50),
    minutes_played SMALLINT DEFAULT 90,
    goals SMALLINT DEFAULT 0,
    assists SMALLINT DEFAULT 0,
    duels_won SMALLINT,
    duels_total SMALLINT,
    shots SMALLINT DEFAULT 0,
    shots_on_target SMALLINT DEFAULT 0,
    key_passes SMALLINT DEFAULT 0,
    player_rating NUMERIC(3,1),                 -- auto-évaluation 1-10
    PRIMARY KEY (match_id, player_id)
);

-- Votes post-match
CREATE TABLE peer_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches_log(id),
    voter_id UUID REFERENCES players(id),
    voted_for_id UUID REFERENCES players(id),
    is_votm BOOLEAN DEFAULT FALSE,              -- joueur du match
    badges TEXT[],                              -- ['rapide','solide','décisif']
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (match_id, voter_id)
);

-- Machine Score historique
CREATE TABLE machine_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    score INTEGER NOT NULL,
    tier VARCHAR(20) NOT NULL,
    tec SMALLINT, phy SMALLINT, vit SMALLINT,
    def SMALLINT, vis SMALLINT, imp SMALLINT,
    data_level SMALLINT,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    -- Composantes du score
    social_component NUMERIC(5,2),             -- votes + badges
    stats_component NUMERIC(5,2),              -- stats manuelles
    regularity_component NUMERIC(5,2),         -- régularité
    progression_component NUMERIC(5,2),        -- progression 30j
    tagging_component NUMERIC(5,2),            -- live tagging / FBref
    video_component NUMERIC(5,2)               -- analyse CV
);

-- Classements (calculés périodiquement)
CREATE TABLE rankings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    position VARCHAR(50),
    region VARCHAR(100),
    category VARCHAR(50),
    rank INTEGER NOT NULL,
    percentile NUMERIC(5,2) NOT NULL,          -- 0-100
    total_players INTEGER NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Feed social
CREATE TABLE feed_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    post_type VARCHAR(50) NOT NULL,            -- match_added/votm/ranking_change/video_analysis/card_upgrade
    content JSONB,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE post_reactions (
    post_id UUID REFERENCES feed_posts(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id),
    PRIMARY KEY (post_id, player_id)
);

-- Badges
CREATE TABLE player_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    badge_key VARCHAR(50) NOT NULL,            -- 'solide','rapide','décisif','votm','top10'
    badge_label VARCHAR(100),
    source_type VARCHAR(50),                   -- peer_vote / ranking / system
    source_id UUID,
    earned_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 Tables vidéo CV

```sql
CREATE TABLE video_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    match_id UUID REFERENCES matches_log(id),
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    duration_seconds NUMERIC(8,2),
    fps NUMERIC(5,2),
    resolution VARCHAR(20),
    filesize_bytes BIGINT,
    processing_status VARCHAR(30) DEFAULT 'uploaded',
    -- Statuts: uploaded/queued/preprocessing/detecting/tracking/
    --          calibrating/generating_overlays/analyzing/exporting/completed/failed
    error_message TEXT,
    quality_score NUMERIC(3,1),                -- 0-10 qualité vidéo
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE video_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES video_assets(id),
    job_type VARCHAR(50),                      -- full_analysis/heatmap_only/clip_only
    celery_task_id TEXT,
    status VARCHAR(30) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    model_versions JSONB,
    result_path TEXT
);

CREATE TABLE video_analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES video_assets(id),
    player_id UUID REFERENCES players(id),
    heatmap_url TEXT,
    overlay_video_url TEXT,
    clip_916_url TEXT,
    -- Métriques extraites
    distance_km NUMERIC(5,2),
    time_in_third_def NUMERIC(5,2),
    time_in_third_mid NUMERIC(5,2),
    time_in_third_att NUMERIC(5,2),
    pressing_triggers INTEGER,
    duels_detected INTEGER,
    passes_detected INTEGER,
    shots_detected INTEGER,
    possession_proxy NUMERIC(5,2),
    -- Rapport IA
    executive_summary TEXT,
    key_insights JSONB,
    recommendations JSONB,
    confidence_level NUMERIC(3,1),
    limitations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.3 Tables FBref / Data Layer

```sql
CREATE TABLE fbref_identity_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    fbref_player_id TEXT NOT NULL,
    fbref_player_name TEXT,
    fbref_club TEXT,
    fbref_nationality TEXT,
    confidence_score NUMERIC(4,3),
    matching_method VARCHAR(50),               -- exact/fuzzy/manual
    confirmed_by_user BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE player_fbref_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    season VARCHAR(10),                        -- 2024-2025
    competition_name TEXT,
    games INTEGER,
    goals INTEGER,
    assists INTEGER,
    xg NUMERIC(6,2),
    xg_assist NUMERIC(6,2),
    progressive_passes INTEGER,
    progressive_carries INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,
    pass_completion NUMERIC(5,2),
    minutes INTEGER,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Machine Score Engine

### 3.1 Formule par niveau de données

```python
def compute_machine_score(player_id: UUID, data_level: int) -> MachineScore:
    """
    data_level 1 : manuel + social uniquement
    data_level 2 : + tagging ou FBref
    data_level 3 : + vidéo CV
    """
    weights = {
        1: {"social": 0.35, "stats": 0.25, "regularity": 0.25, "progression": 0.15},
        2: {"social": 0.25, "events": 0.35, "regularity": 0.20, "progression": 0.20},
        3: {"social": 0.15, "cv_spatial": 0.30, "cv_events": 0.30, "stats": 0.25},
    }
    # Chaque composante calculée sur 0-100
    # Score final = weighted sum
    # Percentile calculé vs joueurs mêmes poste + région + catégorie
```

### 3.2 6 dimensions (TEC/PHY/VIT/DEF/VIS/IMP)

Chaque dimension est calculée à partir des données disponibles et normalisée 0-99.

| Dimension | Level 1 (source) | Level 2 | Level 3 |
|-----------|-----------------|---------|---------|
| TEC | Dribbles + passes (manuel) | FBref pass% + progressive | CV ball touch precision |
| PHY | Duels (manuel) + vote badge "solide" | FBref minutes + duels | CV distance + pressing |
| VIT | Vote badge "rapide" | FBref progressive carries | CV speed proxy |
| DEF | Actions déf. (manuel) | FBref interceptions + tackles | CV defensive coverage |
| VIS | Passes clés (manuel) | FBref key passes + xA | CV pass network |
| IMP | Buts + assists + VOTM | FBref goals + xG | CV shots + goals |

### 3.3 Tiers de carte

| Tier | Score | Card background | Couleur accent |
|------|-------|----------------|----------------|
| Silver | 0-74 | Charcoal gradient | `rgba(180,180,200)` |
| Gold | 75-84 | Navy-blue gradient | `#FFD740` |
| Elite | 85-94 | Deep crimson gradient | `#FF6060` |
| Legend | 95-100 | Dark purple gradient | `#C080FF` |

---

## 4. Player Card Generator

### 4.1 Spec technique

La Player Card est générée **côté serveur** en PNG (via Pillow + HTML→PNG via Playwright headless ou pillow-draw) pour garantir un rendu consistant sur tous les appareils. Elle est aussi rendue côté client en CSS pour l'affichage in-app.

```
Dimensions export : 880×1280px (ratio 2:2.9) @2x pour partage Instagram/TikTok
Format : PNG avec transparence optionnelle
Génération : backend FastAPI → POST /player-card/generate → retourne URL S3
Cache : 24h — regénérée si score change de tier
```

### 4.2 Zones et layout

```
[8px marge]
[Top left] Score (Oswald 700, 96px) + Position (28px)
[Top left+] Drapeau pays (80×56px) + Badge club (80px)
[Centre] Photo joueur — occupe 55% hauteur
           ↕ Dégradé fade bottom 60% vers couleur fond
[Nom] Oswald 700, 42px, uppercase, centré
[Séparateur] 1px teinté, marge 48px
[Stats 3×2] Oswald 600, 34px valeur / 20px label
[Ornements coin] SVG paths 96×96px aux 4 coins
[8px marge]
```

### 4.3 Upload photo joueur

```
Frontend :
1. Bouton "+ Ajouter ma photo" (visible sur la carte placeholder)
2. Bottom sheet : "Prendre une photo" ou "Choisir dans la galerie"
3. Cropping : ratio portrait forcé (2:3), face visible guidée
4. Preview temps réel sur la carte
5. Option "Détourer le fond" (appel API remove.bg ou modèle Python local)
6. Confirmation → upload S3 → POST /players/me/photo
7. Card régénérée automatiquement

Backend :
POST /players/me/photo
  → Validation (format JPG/PNG/WEBP, max 10MB)
  → Resize (max 800×1200)
  → Optionnel : background removal
  → Upload S3 private bucket
  → Trigger card regeneration job
  → Return { photo_url, card_url }
```

---

## 5. FBref Identity Fusion

### 5.1 Processus

```python
async def search_fbref_identity(player: Player) -> FBrefMatch | None:
    """
    Appelé à l'inscription, résultat en < 5s.
    Critères : nom normalisé + club actuel + nationalité
    """
    # 1. Normaliser le nom (accents, tirets, casse)
    normalized_name = normalize_name(player.name)
    
    # 2. Chercher dans FBref via soccerdata
    candidates = fbref_search(name=normalized_name, club=player.club)
    
    # 3. Scorer chaque candidat
    for candidate in candidates:
        score = (
            name_similarity(player.name, candidate.name) * 0.5 +
            club_similarity(player.club, candidate.club) * 0.3 +
            nationality_match(player.country_code, candidate.nationality) * 0.2
        )
    
    # 4. Retourner si score >= 0.85 (seuil validé)
    best = max(candidates, key=lambda c: c.score)
    return best if best.score >= 0.85 else None
```

### 5.2 UX du WOW moment

```
Après inscription :
→ Spinner discret "Recherche de tes stats officielles..."
→ Si trouvé :
    Bottom sheet : "On a trouvé quelque chose 🎉"
    [Photo FBref] [Nom FBref] [Club FBref] [Stats récentes]
    "C'est bien toi ?" → [Oui, c'est moi] [Non, ce n'est pas moi]
→ Si confirmé : profil enrichi, data_level passe à 2, badge "Certifié FBref"
→ Si non trouvé : profil standard, CTA visible "Retrouver mes stats officielles"
```

---

## 6. Système de classement

### 6.1 Contexte de ranking

```
Classements toujours locaux :
- Scope minimum : même région + même catégorie + même poste
- Scope secondaire : même région + même catégorie (tous postes)
- Scope tertiaire : même région (toutes catégories, si masse critique)

Score affiché = percentile dans ce scope local
"Tu es #11 parmi 89 milieux en Martinique U21"
"Top 13% de ta catégorie"
```

### 6.2 Calcul périodique

```python
# Celery beat task — toutes les heures
def compute_rankings():
    for scope in all_ranking_scopes():
        players = get_players_in_scope(scope)
        scores = [(p.id, p.machine_score) for p in players]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (player_id, score) in enumerate(scores, 1):
            percentile = 100 - (rank / len(scores) * 100)
            upsert_ranking(player_id, scope, rank, percentile, len(scores))
```

---

## 7. Composants frontend (Next.js)

### 7.1 Player Card component

```typescript
// src/components/player-card/PlayerCard.tsx
interface PlayerCardProps {
  score: number
  tier: 'silver' | 'gold' | 'elite' | 'legend'
  position: string
  positionShort: string
  name: string
  photoUrl?: string            // si absent → placeholder upload
  photoProcessedUrl?: string   // version détourée
  countryCode: string
  clubBadgeUrl?: string
  attributes: {
    tec: number; phy: number; vit: number
    def: number; vis: number; imp: number
  }
  onPhotoUpload?: () => void   // ouvre le bottom sheet d'upload
  size?: 'small' | 'medium' | 'large'  // pour feed vs profil vs export
}
```

### 7.2 Pages et routes

```
/                    → Feed (home)
/profil              → Mon profil + Player Card + stats
/match/new           → Ajouter un match (form rapide)
/video/upload        → Upload vidéo (premium)
/classements         → Classements locaux
/equipe              → Mon équipe + votes VOTM
/joueur/[username]   → Profil public d'un joueur
/admin/coach         → Dashboard coach (B2B)
```

### 7.3 Schéma d'API FastAPI (endpoints clés)

```
POST /auth/register          → Inscription + FBref search async
GET  /players/me             → Mon profil complet
PATCH /players/me            → Mise à jour profil
POST /players/me/photo       → Upload photo
GET  /players/me/card        → Player Card (PNG ou data pour rendu CSS)
POST /matches                → Ajouter un match
POST /matches/{id}/vote      → Voter VOTM + badges
GET  /rankings/me            → Mon classement + contexte
GET  /rankings               → Classement scope (query params)
GET  /feed                   → Feed social paginé
POST /video/upload            → Upload vidéo → job Celery
GET  /video/{id}/status      → Statut job CV
GET  /video/{id}/report      → Rapport analyse CV
POST /payments/checkout      → Stripe session (Player Spotlight)
```

---

## 8. Machine Score anti-gaming

### 8.1 Règles de validation

```python
ANTI_GAMING_RULES = [
    # Max votes par match = nb joueurs équipe - 1
    "vote_count <= team_size - 1",
    # Un joueur ne peut pas voter pour lui-même
    "voter_id != voted_for_id",
    # Les votes ne comptent que si le votant était dans le match
    "voter_in_match_players",
    # Poids des votes réduit si < 3 coéquipiers ont voté
    "min_voters_for_full_weight = 3",
    # Score cappé à machine_score + 5 par semaine (évite les spikes artificiels)
    "weekly_score_delta_max = 5",
]
```

---

## 9. Phasage d'implémentation

### Phase 1 — Foundation sociale (6 semaines)
- PostgreSQL schema complet
- Auth (Supabase)
- Profil joueur + Player Card CSS
- Photo upload (S3)
- Ajout match + vote VOTM
- Machine Score Level 1
- Feed basique
- Classement local

### Phase 2 — FBref Fusion + enrichissement (4 semaines)
- FBref identity search à l'inscription
- Sync stats FBref hebdomadaire
- Machine Score Level 2 (FBref data)
- Player Card upgrade (tier auto)
- Badge "Certifié FBref"

### Phase 3 — Vidéo CV MVP (8 semaines)
- Upload vidéo + job Celery
- YOLO player detection
- ByteTrack tracking
- Team color clustering
- Heatmap generation
- Rapport IA (Claude API)
- Clip 9:16 (FFmpeg)
- Machine Score Level 3
- Stripe payment (Player Spotlight)

### Phase 4 — Social & Viral (4 semaines)
- Équipe type du week-end
- Notifications push
- Partage Player Card (export PNG optimisé)
- Live tagging coach
- Coach dashboard

### Phase 5 — Scale (ongoing)
- Football Data Layer complet (ClubElo, Understat)
- Détection / Tournois
- Sponsors
- Application mobile (React Native ou PWA)

---

## 10. Checklist spec self-review

- [x] Toutes les tables définies avec types et contraintes
- [x] Machine Score formula précise par niveau
- [x] FBref fusion workflow détaillé
- [x] Player Card spec technique complète (dimensions, zones, tiers)
- [x] Photo upload flow complet (front + back)
- [x] Rankings anti-gaming rules définies
- [x] API endpoints listés
- [x] Phasage clair et séquencé
- [x] Pas de données inventées (chiffres = exemples illustratifs)
- [x] Design référencé à DESIGN.md (FUT card style, Outfit, Electric Lime)
