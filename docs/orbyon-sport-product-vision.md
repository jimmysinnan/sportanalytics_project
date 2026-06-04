# Orbyon Sport — Vision Produit & Architecture Globale

## Ce que les 4 documents disent ensemble

Ces documents ne décrivent pas un outil d'analyse. Ils décrivent une **plateforme sportive sociale** dont la data et l'IA sont le moteur invisible — pas le produit visible.

La phrase centrale du quatrième document résume tout :

> **"La data, l'IA et la computer vision ne sont pas le produit visible. Elles sont le moteur caché qui rend le profil joueur crédible, partageable et monétisable."**

Ce que l'utilisateur vit : **Je joue. Je poste. Je suis noté. Je progresse. Je me montre. Je suis repéré.**  
Ce qui tourne derrière : FBref, StatsBomb, YOLO, ByteTrack, Feature Store, Agent IA.

---

## Positionnement exact

**Nous ne sommes pas** : Wyscout, Hudl, StatsBomb IQ, Opta.  
**Nous sommes** : Tonsser × EA FC cards × Strava × Hudl simplifié — pour le footballeur amateur.

Le marché cible est massivement sous-servi :
- Joueurs amateurs qui veulent être vus et progresser
- Parents qui veulent valoriser l'enfant
- Coachs qui manquent d'outils simples
- Clubs locaux sans budget analyse
- Créateurs de contenu football
- Recruteurs locaux

---

## Les 3 couches du produit

```
┌─────────────────────────────────────────────────────┐
│  COUCHE 1 — App Sociale (ce que l'utilisateur voit) │
│                                                     │
│  Feed / Profil joueur / Player Card                 │
│  Matchs + notes + vote coéquipiers                  │
│  Classements / Équipe type du week-end              │
│  Highlights / Clips 9:16 / Badges                   │
│  Analyse vidéo premium                              │
└─────────────────────────────────────────────────────┘
                          ↑ appelle
┌─────────────────────────────────────────────────────┐
│  COUCHE 2 — Backend API (FastAPI)                   │
│                                                     │
│  Auth / profils / matchs / votes / rankings         │
│  Routers analytics existants (heatmap, tactique…)   │
│  Worker vidéo asynchrone (Celery + Redis)           │
│  Football Data Layer (connecteurs sources)          │
└─────────────────────────────────────────────────────┘
                          ↑ alimente
┌─────────────────────────────────────────────────────┐
│  COUCHE 3 — Intelligence (invisible pour l'user)    │
│                                                     │
│  FBref → référentiel pays/clubs/joueurs             │
│  StatsBomb → training IA, patterns tactiques        │
│  ClubElo, Understat, Football-Data.co.uk            │
│  YOLO + ByteTrack → détection/tracking vidéo        │
│  Feature Store → Machine Score calculé              │
│  Agent Knowledge → rapports IA                     │
└─────────────────────────────────────────────────────┘
```

---

## Le Machine Score — cœur du produit

Le score propriétaire (0-100) est ce qui rend l'app addictive. Il doit combiner :

| Dimension | Source | Poids |
|-----------|--------|-------|
| Note coéquipiers (vote post-match) | App sociale | 30% |
| Note coach | App sociale | 20% |
| Analyse vidéo IA | Module CV | 20% |
| Régularité et engagement | App sociale | 15% |
| Stats manuelles vérifiées | App sociale | 10% |
| Progression sur 30j | Calculé | 5% |

Décomposé en 6 dimensions (comme EA FC) : **TEC / PHY / VIT / DEF / VIS / IMP**

---

## La boucle virale (comme Tonsser)

```
Match joué
    ↓
Joueur ajoute le match (2 min sur l'app)
    ↓
Notification aux coéquipiers : "Vote pour le joueur du match !"
    ↓
Coéquipiers votent → badges attribués → Machine Score mis à jour
    ↓
Équipe type du week-end générée automatiquement
    ↓
Les joueurs sélectionnés partagent le visuel sur Instagram/TikTok
    ↓
De nouveaux joueurs rejoignent pour figurer dans l'équipe type
    ↓
Le coach voit l'intérêt → crée l'équipe officielle
    ↓
Le club rejoint pour structurer l'usage → revenus B2B
```

---

## Différenciation vs Tonsser

| Tonsser | Orbyon Sport |
|---------|-------------|
| Notes coéquipiers | Notes coéquipiers + analyse IA |
| Profil joueur simple | Player Card exportable (EA FC style) |
| Highlights manuels | CV automatique + clip 9:16 annoté |
| Classement basique | Classement enrichi par données FBref/StatsBomb |
| Scouting clubs pros | Scouting + Pack Tournoi + Détection locale |
| Focus Europe du Nord | Focus France/DOM-TOM, puis Afrique, puis monde |

---

## Architecture technique cible

### Base de données (PostgreSQL — à migrer depuis lru_cache)

**Tables sociales (nouvelles) :**
```sql
players           -- profil joueur (name, position, club, score, region)
player_teams      -- appartenance équipe
matches_log       -- matchs ajoutés manuellement
match_players     -- joueurs participants + stats
peer_votes        -- votes coéquipiers post-match
player_badges     -- badges attribués
machine_scores    -- historique du score par joueur
highlights        -- vidéos/clips uploadés
feed_posts        -- activité du feed social
rankings          -- classements calculés (par poste/région/catégorie)
team_of_week      -- équipe type générée
```

**Tables vidéo CV (à créer) :**
```sql
video_assets      -- fichiers uploadés
video_jobs        -- statut traitement async
video_detections  -- détections frame par frame
video_tracks      -- tracking joueurs
video_reports     -- rapport IA généré
```

**Tables Data Layer (à créer) :**
```sql
canonical_players     -- joueurs normalisés (FBref + autres)
canonical_teams       -- clubs normalisés
canonical_competitions-- compétitions normalisées
source_mappings       -- correspondances cross-sources
raw_payloads          -- données brutes tracées
```

### Stack complémentaire à ajouter

```
PostgreSQL         → base de données (remplace lru_cache)
Redis              → queue jobs vidéo + cache
Celery             → workers CV async
OpenCV + YOLO      → détection/tracking vidéo
Stripe             → paiement Player Spotlight
Supabase Auth      → authentification (ou custom JWT)
S3/CloudFlare R2   → stockage vidéos et assets
```

---

## Phasage de développement

### Phase 0 — Player Spotlight Service (10 jours, 0 code app)
**Objectif : valider la demande avant de coder.**

- Landing page simple (Next.js ou même Notion + Stripe)
- Joueur envoie vidéo via WhatsApp ou formulaire
- Tu génères semi-manuellement : Player Card + mini-rapport + clip 9:16
- Livraison par WhatsApp/email
- Prix : 49€ → valide que les gens paient

Cible : Martinique, clubs locaux, joueurs connus.

### Phase 1 — App sociale MVP (6-8 semaines)
**Objectif : boucle virale joueur-coéquipier.**

- Auth (email + téléphone)
- Profil joueur + Player Card
- Ajout match (simple)
- Vote coéquipiers post-match
- Machine Score basique
- Classement par poste + région
- Partage Player Card
- Feed activité

### Phase 2 — Analyse vidéo automatisée (8-12 semaines)
**Objectif : feature premium différenciante.**

- Upload vidéo (<5min, 720p/1080p)
- Job Celery async (YOLO + ByteTrack + team clustering)
- Heatmap + overlay + rapport IA
- Clip 9:16 auto-généré
- Machine Score enrichi avec données CV
- Paiement Stripe (crédits)

### Phase 3 — Football Data Layer (parallèle / continu)
**Objectif : enrichir l'intelligence derrière le score.**

- PostgreSQL + schema canonique
- FBref connector (pays, clubs, joueurs, référentiel)
- StatsBomb training pipeline (features IA)
- ClubElo + Understat
- Machine Score v2 (enrichi par données publiques)

### Phase 4 — Clubs & Coachs (B2B)
**Objectif : revenus récurrents stables.**

- Dashboard coach (ce qu'on a construit en Next.js)
- Pack Club (plusieurs équipes, plusieurs coachs)
- Pack Tournoi (événementiel)
- API intégration (pour clubs structurés)

### Phase 5 — Détection / Sponsors / Média
**Objectif : devenir le passage obligé.**

- Sélections mensuelles
- Partenariats marques sportives
- "Team of the Week by [Sponsor]"
- Événements physiques

---

## Premier livrable prioritaire

Avant tout, créer le **Player Spotlight MVP semi-manuel** :

1. Joueur → envoie vidéo (WhatsApp ou formulaire)
2. Backend → Player Card generator (Next.js API ou script Python)
3. Backend → Rapport IA (Claude API sur les stats manuelles)
4. Backend → Clip 9:16 (FFmpeg + overlay Python)
5. Livraison → PDF + MP4 par email

Ce flux peut tourner avec ce qu'on a déjà + quelques ajouts.
