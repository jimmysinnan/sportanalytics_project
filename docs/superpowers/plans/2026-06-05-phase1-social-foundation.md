# Orbyon Sport — Phase 1: Social Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire la couche sociale complète d'Orbyon Sport : auth, profil joueur, Player Card FUT-style avec photo, ajout match, vote VOTM, Machine Score Level 1, classements locaux et feed social.

**Architecture:** Extension du backend FastAPI existant avec SQLAlchemy + PostgreSQL. Nouvelles pages Next.js mobile-first. Player Card rendue en CSS (React) + export PNG via html2canvas. Auth via Supabase JWT.

**Tech Stack:** FastAPI · SQLAlchemy 2.0 async · PostgreSQL (Supabase) · Alembic · Next.js 14 App Router · Outfit font · html2canvas · Supabase Auth · Supabase Storage

---

## Structure des fichiers

```
backend/
├── db/
│   ├── __init__.py
│   ├── session.py          ← engine SQLAlchemy async
│   ├── models.py           ← tous les modèles ORM
│   └── migrations/         ← Alembic
├── routers/
│   ├── social/
│   │   ├── __init__.py
│   │   ├── auth.py         ← POST /auth/register, /auth/me
│   │   ├── profiles.py     ← GET/PATCH /players/me, photo upload
│   │   ├── matches.py      ← POST /matches, GET /matches
│   │   ├── votes.py        ← POST /matches/{id}/vote
│   │   ├── feed.py         ← GET /feed
│   │   └── rankings.py     ← GET /rankings/me, /rankings
│   └── (existing routers unchanged)
├── services/
│   ├── machine_score.py    ← calcul Machine Score L1
│   ├── rankings.py         ← calcul classements percentile
│   └── card_generator.py   ← génération Player Card PNG (Phase 2)
├── auth.py                 ← vérification JWT Supabase
└── requirements.txt        ← + sqlalchemy asyncpg alembic supabase

frontend/src/
├── app/
│   ├── (social)/           ← group layout mobile-first
│   │   ├── layout.tsx      ← bottom nav, social shell
│   │   ├── feed/page.tsx
│   │   ├── profil/page.tsx ← social profile (≠ analytics /profil)
│   │   ├── match/
│   │   │   └── new/page.tsx
│   │   ├── vote/[matchId]/page.tsx
│   │   ├── classements/page.tsx
│   │   └── equipe/page.tsx
├── components/
│   ├── player-card/
│   │   ├── PlayerCard.tsx      ← composant FUT card
│   │   ├── PlayerCardTiers.ts  ← couleurs par tier
│   │   └── PhotoUpload.tsx     ← bottom sheet upload photo
│   ├── social/
│   │   ├── FeedPost.tsx
│   │   ├── MatchItem.tsx
│   │   ├── VoteSheet.tsx
│   │   └── RankingRow.tsx
│   └── ui/
│       ├── BottomSheet.tsx
│       └── Spinner.tsx
└── lib/
    ├── social-api.ts       ← client API social (séparé de api.ts analytics)
    ├── auth.ts             ← Supabase auth helpers
    └── social-types.ts     ← types TypeScript social
```

---

## Task 1 — PostgreSQL + SQLAlchemy + Alembic

**Files:**
- Create: `backend/db/__init__.py`
- Create: `backend/db/session.py`
- Create: `backend/db/models.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1 : Ajouter les dépendances**

Modifier `backend/requirements.txt` — ajouter à la fin :
```
sqlalchemy>=2.0
asyncpg>=0.29
alembic>=1.13
supabase>=2.4
python-jose[cryptography]>=3.3
python-multipart>=0.0.10
pillow>=10.0
boto3>=1.34
```

- [ ] **Step 2 : Créer `backend/db/__init__.py`** (vide)

- [ ] **Step 3 : Créer `backend/db/session.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/orbyon_sport"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

- [ ] **Step 4 : Créer `backend/db/models.py`**

```python
from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from db.session import Base


def new_uuid():
    return str(uuid4())


class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    auth_id: Mapped[str] = mapped_column(sa.Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    position: Mapped[Optional[str]] = mapped_column(sa.String(50))
    position_short: Mapped[Optional[str]] = mapped_column(sa.String(10))
    club: Mapped[Optional[str]] = mapped_column(sa.String(100))
    region: Mapped[Optional[str]] = mapped_column(sa.String(100))
    category: Mapped[Optional[str]] = mapped_column(sa.String(50))
    country_code: Mapped[Optional[str]] = mapped_column(sa.CHAR(2))
    photo_url: Mapped[Optional[str]] = mapped_column(sa.Text)
    machine_score: Mapped[int] = mapped_column(sa.Integer, default=0)
    machine_score_tier: Mapped[str] = mapped_column(sa.String(20), default="silver")
    data_level: Mapped[int] = mapped_column(sa.SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    matches: Mapped[list["MatchPlayer"]] = relationship(back_populates="player")
    votes_cast: Mapped[list["PeerVote"]] = relationship("PeerVote", foreign_keys="PeerVote.voter_id", back_populates="voter")
    votes_received: Mapped[list["PeerVote"]] = relationship("PeerVote", foreign_keys="PeerVote.voted_for_id", back_populates="voted_for")
    scores: Mapped[list["MachineScoreHistory"]] = relationship(back_populates="player")
    badges: Mapped[list["PlayerBadge"]] = relationship(back_populates="player")


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    club: Mapped[Optional[str]] = mapped_column(sa.String(100))
    region: Mapped[Optional[str]] = mapped_column(sa.String(100))
    category: Mapped[Optional[str]] = mapped_column(sa.String(50))
    coach_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    invite_code: Mapped[Optional[str]] = mapped_column(sa.String(8), unique=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    players: Mapped[list["TeamPlayer"]] = relationship(back_populates="team")
    matches: Mapped[list["MatchLog"]] = relationship(back_populates="team")


class TeamPlayer(Base):
    __tablename__ = "team_players"

    team_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(sa.String(20), default="player")
    joined_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    team: Mapped["Team"] = relationship(back_populates="players")
    player: Mapped["Player"] = relationship()


class MatchLog(Base):
    __tablename__ = "matches_log"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    team_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("teams.id"))
    opponent_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    home_score: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    away_score: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    match_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    competition: Mapped[Optional[str]] = mapped_column(sa.String(100))
    is_home: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    team: Mapped[Optional["Team"]] = relationship(back_populates="matches")
    players: Mapped[list["MatchPlayer"]] = relationship(back_populates="match")
    votes: Mapped[list["PeerVote"]] = relationship(back_populates="match")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("matches_log.id", ondelete="CASCADE"), primary_key=True)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[Optional[str]] = mapped_column(sa.String(50))
    minutes_played: Mapped[int] = mapped_column(sa.SmallInteger, default=90)
    goals: Mapped[int] = mapped_column(sa.SmallInteger, default=0)
    assists: Mapped[int] = mapped_column(sa.SmallInteger, default=0)
    duels_won: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    duels_total: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    shots: Mapped[int] = mapped_column(sa.SmallInteger, default=0)
    key_passes: Mapped[int] = mapped_column(sa.SmallInteger, default=0)
    player_rating: Mapped[Optional[float]] = mapped_column(sa.Numeric(3, 1))

    match: Mapped["MatchLog"] = relationship(back_populates="players")
    player: Mapped["Player"] = relationship(back_populates="matches")


class PeerVote(Base):
    __tablename__ = "peer_votes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("matches_log.id"))
    voter_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    voted_for_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    is_votm: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    badges: Mapped[list] = mapped_column(ARRAY(sa.Text), default=list)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (sa.UniqueConstraint("match_id", "voter_id"),)

    match: Mapped["MatchLog"] = relationship(back_populates="votes")
    voter: Mapped["Player"] = relationship("Player", foreign_keys=[voter_id], back_populates="votes_cast")
    voted_for: Mapped["Player"] = relationship("Player", foreign_keys=[voted_for_id], back_populates="votes_received")


class MachineScoreHistory(Base):
    __tablename__ = "machine_scores"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    score: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    tier: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    tec: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    phy: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    vit: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    def_: Mapped[Optional[int]] = mapped_column("def", sa.SmallInteger)
    vis: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    imp: Mapped[Optional[int]] = mapped_column(sa.SmallInteger)
    social_component: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    stats_component: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    regularity_component: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    progression_component: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    computed_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    player: Mapped["Player"] = relationship(back_populates="scores")


class PlayerBadge(Base):
    __tablename__ = "player_badges"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    badge_key: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    badge_label: Mapped[Optional[str]] = mapped_column(sa.String(100))
    source_type: Mapped[Optional[str]] = mapped_column(sa.String(50))
    earned_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)

    player: Mapped["Player"] = relationship(back_populates="badges")


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    position: Mapped[Optional[str]] = mapped_column(sa.String(50))
    region: Mapped[Optional[str]] = mapped_column(sa.String(100))
    category: Mapped[Optional[str]] = mapped_column(sa.String(50))
    rank: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    percentile: Mapped[float] = mapped_column(sa.Numeric(5, 2), nullable=False)
    total_players: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)


class FeedPost(Base):
    __tablename__ = "feed_posts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    player_id: Mapped[str] = mapped_column(UUID(as_uuid=False), sa.ForeignKey("players.id"))
    post_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    content: Mapped[Optional[dict]] = mapped_column(JSONB)
    likes_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=datetime.utcnow)
```

- [ ] **Step 5 : Initialiser Alembic**

```bash
cd backend
pip install alembic asyncpg sqlalchemy supabase python-jose[cryptography]
alembic init db/migrations
```

Modifier `backend/db/migrations/env.py` — remplacer les lignes `target_metadata` :
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db.session import Base
from db import models  # noqa — force import de tous les modèles
target_metadata = Base.metadata
```

Modifier `backend/db/migrations/alembic.ini` (ou `alembic.ini` à la racine) :
```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/orbyon_sport
```

- [ ] **Step 6 : Créer et appliquer la migration initiale**

```bash
# Démarrer PostgreSQL en local (Docker)
docker run -d --name orbyon-db \
  -e POSTGRES_DB=orbyon_sport \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 postgres:16

# Générer la migration
cd backend
alembic revision --autogenerate -m "initial social schema"
alembic upgrade head
```

Résultat attendu : `INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, initial social schema`

- [ ] **Step 7 : Commit**

```bash
git add backend/db/ backend/requirements.txt
git commit -m "feat(db): schema PostgreSQL + SQLAlchemy models + Alembic migration"
```

---

## Task 2 — Auth Supabase (vérification JWT)

**Files:**
- Create: `backend/auth.py`
- Create: `backend/.env.example`

- [ ] **Step 1 : Créer `backend/auth.py`**

```python
from __future__ import annotations
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import Player

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")
security = HTTPBearer()


async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Player:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"],
                             audience="authenticated")
        auth_id: str = payload.get("sub")
        if not auth_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(Player).where(Player.auth_id == auth_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not registered")
    return player
```

- [ ] **Step 2 : Créer `backend/.env.example`**

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/orbyon_sport
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-dashboard
SUPABASE_STORAGE_BUCKET=orbyon-photos
```

- [ ] **Step 3 : Créer `backend/routers/social/__init__.py`** (vide)

- [ ] **Step 4 : Vérifier que l'import fonctionne**

```bash
cd backend
python -c "from auth import get_current_player; print('ok')"
# Attendu : ok
```

- [ ] **Step 5 : Commit**

```bash
git add backend/auth.py backend/.env.example backend/routers/social/
git commit -m "feat(auth): verification JWT Supabase + dependency FastAPI"
```

---

## Task 3 — Router social/profiles (register + profil)

**Files:**
- Create: `backend/routers/social/profiles.py`
- Modify: `backend/main.py`

- [ ] **Step 1 : Créer `backend/routers/social/profiles.py`**

```python
from __future__ import annotations
import os, uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import Player, MachineScoreHistory, PlayerBadge
from auth import get_current_player

router = APIRouter(prefix="/players", tags=["social-players"])

POSITION_SHORT_MAP = {
    "Gardien": "GB", "Défenseur Central": "DC", "Latéral Droit": "LD",
    "Latéral Gauche": "LG", "Milieu Défensif": "MD", "Milieu Central": "MC",
    "Milieu Offensif": "MO", "Ailier Droit": "AD", "Ailier Gauche": "AG",
    "Attaquant": "BU", "Avant-Centre": "AC",
}

TIER_FROM_SCORE = {
    range(0, 75): "silver",
    range(75, 85): "gold",
    range(85, 95): "elite",
    range(95, 101): "legend",
}


def score_to_tier(score: int) -> str:
    for r, tier in TIER_FROM_SCORE.items():
        if score in r:
            return tier
    return "silver"


class RegisterRequest(BaseModel):
    name: str
    username: str
    position: str | None = None
    club: str | None = None
    region: str | None = None
    category: str | None = None
    country_code: str | None = None

    @field_validator("username")
    @classmethod
    def username_clean(cls, v: str) -> str:
        v = v.strip().lower().replace(" ", "_")
        if len(v) < 3:
            raise ValueError("username trop court (min 3 caractères)")
        return v


class PlayerOut(BaseModel):
    id: str
    name: str
    username: str
    position: str | None
    position_short: str | None
    club: str | None
    region: str | None
    category: str | None
    country_code: str | None
    photo_url: str | None
    machine_score: int
    machine_score_tier: str
    data_level: int

    model_config = {"from_attributes": True}


@router.post("/register", response_model=PlayerOut, status_code=201)
async def register_player(
    body: RegisterRequest,
    credentials=Depends(__import__("fastapi.security", fromlist=["HTTPBearer"]).HTTPBearer()),
    db: AsyncSession = Depends(get_db),
):
    from jose import jwt as _jwt
    token = credentials.credentials
    try:
        payload = _jwt.decode(token, os.environ.get("SUPABASE_JWT_SECRET", ""),
                              algorithms=["HS256"], audience="authenticated")
        auth_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "Token invalide")

    # Vérifier username unique
    existing = await db.execute(select(Player).where(Player.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Ce username est déjà pris")

    pos_short = POSITION_SHORT_MAP.get(body.position or "", "")
    player = Player(
        auth_id=auth_id,
        name=body.name,
        username=body.username,
        position=body.position,
        position_short=pos_short or None,
        club=body.club,
        region=body.region,
        category=body.category,
        country_code=body.country_code,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


@router.get("/me", response_model=PlayerOut)
async def get_my_profile(
    player: Player = Depends(get_current_player),
):
    return player


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    position: str | None = None
    club: str | None = None
    region: str | None = None
    category: str | None = None
    country_code: str | None = None


@router.patch("/me", response_model=PlayerOut)
async def update_profile(
    body: UpdateProfileRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    if body.name is not None:
        player.name = body.name
    if body.position is not None:
        player.position = body.position
        player.position_short = POSITION_SHORT_MAP.get(body.position, "") or None
    if body.club is not None:
        player.club = body.club
    if body.region is not None:
        player.region = body.region
    if body.category is not None:
        player.category = body.category
    if body.country_code is not None:
        player.country_code = body.country_code
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


@router.get("/{username}", response_model=PlayerOut)
async def get_player_by_username(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Player).where(Player.username == username))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(404, "Joueur introuvable")
    return player
```

- [ ] **Step 2 : Enregistrer le router dans `backend/main.py`**

Lire `backend/main.py` puis ajouter après les imports existants :
```python
from routers.social.profiles import router as social_profiles_router
app.include_router(social_profiles_router)
```

- [ ] **Step 3 : Tester l'endpoint register (sans auth pour le smoke test)**

```bash
cd backend
uvicorn main:app --reload --port 8000
# Dans un autre terminal :
curl http://localhost:8000/docs
# Vérifier que /players/register apparaît dans la Swagger UI
```

- [ ] **Step 4 : Commit**

```bash
git add backend/routers/social/profiles.py backend/main.py
git commit -m "feat(social): router profils - register, get/update profil, lookup username"
```

---

## Task 4 — Upload photo joueur (Supabase Storage)

**Files:**
- Create: `backend/services/storage.py`
- Modify: `backend/routers/social/profiles.py`

- [ ] **Step 1 : Créer `backend/services/storage.py`**

```python
from __future__ import annotations
import os, io, uuid
from PIL import Image

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "orbyon-photos")
MAX_PHOTO_SIDE = 800  # px max côté le plus long


def resize_photo(data: bytes) -> bytes:
    """Redimensionne l'image à MAX_PHOTO_SIDE max, conserve le ratio."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((MAX_PHOTO_SIDE, MAX_PHOTO_SIDE * 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()


async def upload_player_photo(player_id: str, file_data: bytes, content_type: str) -> str:
    """
    Upload la photo vers Supabase Storage.
    Retourne l'URL publique.
    Fallback local si pas de Supabase configuré (dev).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        # Mode dev : sauvegarder localement
        path = f"/tmp/orbyon_photos/{player_id}.jpg"
        os.makedirs("/tmp/orbyon_photos", exist_ok=True)
        with open(path, "wb") as f:
            f.write(file_data)
        return f"file://{path}"

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    filename = f"{player_id}/{uuid.uuid4()}.jpg"
    client.storage.from_(BUCKET).upload(
        path=filename,
        file=file_data,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
```

- [ ] **Step 2 : Ajouter l'endpoint photo dans `backend/routers/social/profiles.py`**

Ajouter à la fin du fichier :
```python
@router.post("/me/photo", response_model=PlayerOut)
async def upload_photo(
    file: UploadFile = File(...),
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    from services.storage import resize_photo, upload_player_photo

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Format accepté : JPG, PNG, WEBP")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Fichier trop lourd (max 10MB)")

    resized = resize_photo(data)
    url = await upload_player_photo(player.id, resized, "image/jpeg")

    player.photo_url = url
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player
```

- [ ] **Step 3 : Vérifier syntaxe**

```bash
cd backend && python -m py_compile routers/social/profiles.py services/storage.py && echo "ok"
```

- [ ] **Step 4 : Commit**

```bash
git add backend/services/storage.py backend/routers/social/profiles.py
git commit -m "feat(social): upload photo joueur - resize + Supabase Storage"
```

---

## Task 5 — Router matches + votes

**Files:**
- Create: `backend/routers/social/matches.py`
- Create: `backend/routers/social/votes.py`

- [ ] **Step 1 : Créer `backend/routers/social/matches.py`**

```python
from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.session import get_db
from db.models import MatchLog, MatchPlayer, Player, Team, FeedPost
from auth import get_current_player

router = APIRouter(prefix="/matches", tags=["social-matches"])


class MatchPlayerInput(BaseModel):
    player_id: str
    position: str | None = None
    minutes_played: int = 90
    goals: int = 0
    assists: int = 0
    duels_won: int | None = None
    duels_total: int | None = None
    shots: int = 0
    key_passes: int = 0
    player_rating: float | None = None


class CreateMatchRequest(BaseModel):
    opponent_name: str
    home_score: int | None = None
    away_score: int | None = None
    match_date: date
    competition: str | None = None
    is_home: bool = True
    team_id: str | None = None
    players: list[MatchPlayerInput] = []


class MatchOut(BaseModel):
    id: str
    opponent_name: str
    home_score: int | None
    away_score: int | None
    match_date: date
    competition: str | None
    is_home: bool
    model_config = {"from_attributes": True}


@router.post("", response_model=MatchOut, status_code=201)
async def create_match(
    body: CreateMatchRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    match = MatchLog(
        team_id=body.team_id,
        opponent_name=body.opponent_name,
        home_score=body.home_score,
        away_score=body.away_score,
        match_date=body.match_date,
        competition=body.competition,
        is_home=body.is_home,
        created_by=player.id,
    )
    db.add(match)
    await db.flush()

    # Ajouter le créateur si non dans la liste
    player_ids_in = {p.player_id for p in body.players}
    if player.id not in player_ids_in:
        body.players.append(MatchPlayerInput(player_id=player.id))

    for p_input in body.players:
        mp = MatchPlayer(
            match_id=match.id,
            player_id=p_input.player_id,
            position=p_input.position,
            minutes_played=p_input.minutes_played,
            goals=p_input.goals,
            assists=p_input.assists,
            duels_won=p_input.duels_won,
            duels_total=p_input.duels_total,
            shots=p_input.shots,
            key_passes=p_input.key_passes,
            player_rating=p_input.player_rating,
        )
        db.add(mp)

    # Post feed
    post = FeedPost(
        player_id=player.id,
        post_type="match_added",
        content={
            "match_id": match.id,
            "opponent": body.opponent_name,
            "score": f"{body.home_score}-{body.away_score}" if body.home_score is not None else None,
        },
    )
    db.add(post)
    await db.commit()
    await db.refresh(match)
    return match


@router.get("/me", response_model=list[MatchOut])
async def get_my_matches(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MatchLog)
        .join(MatchPlayer, MatchPlayer.match_id == MatchLog.id)
        .where(MatchPlayer.player_id == player.id)
        .order_by(MatchLog.match_date.desc())
        .limit(20)
    )
    return result.scalars().all()
```

- [ ] **Step 2 : Créer `backend/routers/social/votes.py`**

```python
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.session import get_db
from db.models import PeerVote, MatchLog, MatchPlayer, Player, PlayerBadge, FeedPost
from auth import get_current_player
from services.machine_score import recompute_machine_score

router = APIRouter(prefix="/matches", tags=["social-votes"])

VALID_BADGES = {
    "rapide", "solide", "technique", "décisif", "collectif",
    "vision", "muraille", "clutch", "leader", "régulier"
}


class VoteRequest(BaseModel):
    voted_for_id: str
    is_votm: bool = False
    badges: list[str] = []


@router.post("/{match_id}/vote", status_code=201)
async def cast_vote(
    match_id: str,
    body: VoteRequest,
    voter: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    # Vérifier que le match existe
    match = await db.get(MatchLog, match_id)
    if not match:
        raise HTTPException(404, "Match introuvable")

    # Vérifier que le votant était dans le match
    voter_in_match = await db.execute(
        select(MatchPlayer).where(
            MatchPlayer.match_id == match_id,
            MatchPlayer.player_id == voter.id,
        )
    )
    if not voter_in_match.scalar_one_or_none():
        raise HTTPException(403, "Tu n'as pas participé à ce match")

    # Vérifier que le votant ne vote pas pour lui-même
    if body.voted_for_id == voter.id:
        raise HTTPException(400, "Tu ne peux pas voter pour toi-même")

    # Vérifier le vote unique par match
    existing = await db.execute(
        select(PeerVote).where(
            PeerVote.match_id == match_id,
            PeerVote.voter_id == voter.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Tu as déjà voté pour ce match")

    # Valider les badges
    invalid = set(body.badges) - VALID_BADGES
    if invalid:
        raise HTTPException(400, f"Badges invalides : {invalid}")

    vote = PeerVote(
        match_id=match_id,
        voter_id=voter.id,
        voted_for_id=body.voted_for_id,
        is_votm=body.is_votm,
        badges=body.badges,
    )
    db.add(vote)

    # Sauvegarder les badges obtenus
    for badge_key in body.badges:
        badge = PlayerBadge(
            player_id=body.voted_for_id,
            badge_key=badge_key,
            badge_label=badge_key.capitalize(),
            source_type="peer_vote",
        )
        db.add(badge)

    if body.is_votm:
        post = FeedPost(
            player_id=body.voted_for_id,
            post_type="votm",
            content={"match_id": match_id, "voter_id": voter.id},
        )
        db.add(post)

    await db.commit()

    # Recalculer le Machine Score du joueur voté
    await recompute_machine_score(body.voted_for_id, db)

    return {"status": "vote enregistré"}
```

- [ ] **Step 3 : Ajouter les routers dans `backend/main.py`**

```python
from routers.social.matches import router as social_matches_router
from routers.social.votes import router as social_votes_router
app.include_router(social_matches_router)
app.include_router(social_votes_router)
```

- [ ] **Step 4 : Commit**

```bash
git add backend/routers/social/matches.py backend/routers/social/votes.py backend/main.py
git commit -m "feat(social): routers matches (create/get) et votes VOTM + badges"
```

---

## Task 6 — Machine Score Level 1

**Files:**
- Create: `backend/services/machine_score.py`

- [ ] **Step 1 : Créer `backend/services/machine_score.py`**

```python
from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models import Player, MatchPlayer, PeerVote, MachineScoreHistory, PlayerBadge


def score_to_tier(score: int) -> str:
    if score >= 95:
        return "legend"
    if score >= 85:
        return "elite"
    if score >= 75:
        return "gold"
    return "silver"


def _clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, v))


async def recompute_machine_score(player_id: str, db: AsyncSession) -> int:
    """
    Calcule et sauvegarde le Machine Score Level 1.
    Formule : social 35% + stats 25% + régularité 25% + progression 15%
    Retourne le nouveau score (0-100).
    """
    # ── Composante sociale (votes + badges) ──────────────────────────────────
    votes_result = await db.execute(
        select(func.count(PeerVote.id), func.sum(PeerVote.is_votm.cast(int)))
        .where(PeerVote.voted_for_id == player_id)
    )
    total_votes, total_votm = votes_result.one()
    total_votes = total_votes or 0
    total_votm = total_votm or 0

    badges_result = await db.execute(
        select(func.count(PlayerBadge.id)).where(PlayerBadge.player_id == player_id)
    )
    total_badges = badges_result.scalar() or 0

    # social_score : max 100 — votes normalisés sur 20 max + VOTM bonus + badges
    vote_component = _clamp(total_votes / 20 * 60)
    votm_component = _clamp(total_votm * 10, hi=25)
    badge_component = _clamp(total_badges * 3, hi=15)
    social_score = _clamp(vote_component + votm_component + badge_component)

    # ── Composante stats (saisies manuelles) ─────────────────────────────────
    stats_result = await db.execute(
        select(
            func.sum(MatchPlayer.goals),
            func.sum(MatchPlayer.assists),
            func.avg(MatchPlayer.player_rating),
            func.sum(MatchPlayer.key_passes),
        ).where(MatchPlayer.player_id == player_id)
    )
    goals, assists, avg_rating, key_passes = stats_result.one()
    goals = goals or 0
    assists = assists or 0
    avg_rating = float(avg_rating or 5.0)
    key_passes = key_passes or 0

    stats_score = _clamp(
        (goals * 5) + (assists * 3) + ((avg_rating - 5) * 8) + (key_passes * 2)
    )

    # ── Régularité (matchs joués) ─────────────────────────────────────────────
    matches_result = await db.execute(
        select(func.count(MatchPlayer.match_id))
        .where(MatchPlayer.player_id == player_id)
    )
    total_matches = matches_result.scalar() or 0
    regularity_score = _clamp(total_matches / 15 * 100)  # 15 matchs = max

    # ── Progression (évolution sur 30 jours) ─────────────────────────────────
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    prev_score_result = await db.execute(
        select(MachineScoreHistory.score)
        .where(
            MachineScoreHistory.player_id == player_id,
            MachineScoreHistory.computed_at < thirty_days_ago,
        )
        .order_by(MachineScoreHistory.computed_at.desc())
        .limit(1)
    )
    prev_score = prev_score_result.scalar() or 0

    # ── Score final ────────────────────────────────────────────────────────────
    final_score = int(
        social_score * 0.35 +
        stats_score * 0.25 +
        regularity_score * 0.25 +
        max(0, (50 + (prev_score * 0.15)))  # progression baseline
    )
    final_score = _clamp(final_score, lo=0, hi=100)

    # 6 dimensions (estimation depuis les stats disponibles)
    tec = int(_clamp(stats_score * 0.8 + badge_component))
    phy = int(_clamp(vote_component * 0.6 + regularity_score * 0.4))
    vit = int(_clamp(50 + vote_component * 0.3))  # approximation Level 1
    def_ = int(_clamp(social_score * 0.5 + regularity_score * 0.5))
    vis = int(_clamp((key_passes or 0) * 4 + stats_score * 0.3))
    imp = int(_clamp(goals * 6 + assists * 4 + total_votm * 8))

    tier = score_to_tier(final_score)

    # Sauvegarder l'historique
    history = MachineScoreHistory(
        player_id=player_id,
        score=final_score,
        tier=tier,
        tec=tec, phy=phy, vit=vit, def_=def_, vis=vis, imp=imp,
        social_component=round(social_score, 2),
        stats_component=round(stats_score, 2),
        regularity_component=round(regularity_score, 2),
        progression_component=0.0,
    )
    db.add(history)

    # Mettre à jour le player
    player = await db.get(Player, player_id)
    if player:
        player.machine_score = final_score
        player.machine_score_tier = tier
        db.add(player)

    await db.commit()
    return final_score
```

- [ ] **Step 2 : Vérifier syntaxe**

```bash
cd backend && python -m py_compile services/machine_score.py && echo "ok"
```

- [ ] **Step 3 : Commit**

```bash
git add backend/services/machine_score.py
git commit -m "feat(social): Machine Score Level 1 - social 35% + stats 25% + regularite 25% + progression 15%"
```

---

## Task 7 — Router rankings + feed

**Files:**
- Create: `backend/routers/social/rankings.py`
- Create: `backend/routers/social/feed.py`

- [ ] **Step 1 : Créer `backend/routers/social/rankings.py`**

```python
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from db.session import get_db
from db.models import Player, Ranking
from auth import get_current_player

router = APIRouter(prefix="/rankings", tags=["social-rankings"])


class RankingOut(BaseModel):
    player_id: str
    rank: int
    percentile: float
    total_players: int
    position: str | None
    region: str | None
    category: str | None
    model_config = {"from_attributes": True}


class PlayerRankRow(BaseModel):
    rank: int
    percentile: float
    player_id: str
    name: str
    username: str
    position_short: str | None
    club: str | None
    machine_score: int
    machine_score_tier: str
    photo_url: str | None
    model_config = {"from_attributes": True}


@router.get("/me", response_model=RankingOut | None)
async def get_my_ranking(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ranking)
        .where(Ranking.player_id == player.id)
        .order_by(Ranking.computed_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("", response_model=list[PlayerRankRow])
async def get_rankings(
    region: str | None = Query(None),
    category: str | None = Query(None),
    position: str | None = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Classement local par région + catégorie + poste.
    Tous les filtres sont optionnels — au moins region recommandé.
    """
    query = (
        select(Player)
        .where(Player.machine_score > 0)
        .order_by(Player.machine_score.desc())
        .limit(limit)
    )
    if region:
        query = query.where(Player.region == region)
    if category:
        query = query.where(Player.category == category)
    if position:
        query = query.where(Player.position == position)

    result = await db.execute(query)
    players = result.scalars().all()

    total = len(players)
    rows = []
    for i, p in enumerate(players, 1):
        percentile = round(100 - (i / total * 100), 1) if total > 1 else 100.0
        rows.append(PlayerRankRow(
            rank=i,
            percentile=percentile,
            player_id=p.id,
            name=p.name,
            username=p.username,
            position_short=p.position_short,
            club=p.club,
            machine_score=p.machine_score,
            machine_score_tier=p.machine_score_tier,
            photo_url=p.photo_url,
        ))
    return rows
```

- [ ] **Step 2 : Créer `backend/routers/social/feed.py`**

```python
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import datetime
from db.session import get_db
from db.models import FeedPost, Player
from auth import get_current_player

router = APIRouter(prefix="/feed", tags=["social-feed"])


class FeedPostOut(BaseModel):
    id: str
    post_type: str
    content: dict | None
    likes_count: int
    created_at: datetime
    player_name: str
    player_username: str
    player_photo_url: str | None
    player_score: int
    player_tier: str
    model_config = {"from_attributes": True}


@router.get("", response_model=list[FeedPostOut])
async def get_feed(
    limit: int = Query(20, le=50),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_player: Player = Depends(get_current_player),
):
    result = await db.execute(
        select(FeedPost, Player)
        .join(Player, Player.id == FeedPost.player_id)
        .order_by(FeedPost.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
    out = []
    for post, player in rows:
        out.append(FeedPostOut(
            id=post.id,
            post_type=post.post_type,
            content=post.content,
            likes_count=post.likes_count,
            created_at=post.created_at,
            player_name=player.name,
            player_username=player.username,
            player_photo_url=player.photo_url,
            player_score=player.machine_score,
            player_tier=player.machine_score_tier,
        ))
    return out


@router.post("/{post_id}/like", status_code=204)
async def like_post(
    post_id: str,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(FeedPost, post_id)
    if post:
        post.likes_count += 1
        db.add(post)
        await db.commit()
```

- [ ] **Step 3 : Enregistrer les 4 routers sociaux restants dans `backend/main.py`**

```python
from routers.social.rankings import router as social_rankings_router
from routers.social.feed import router as social_feed_router
app.include_router(social_rankings_router)
app.include_router(social_feed_router)
```

- [ ] **Step 4 : Test complet de l'API**

```bash
cd backend && uvicorn main:app --reload --port 8000
curl http://localhost:8000/docs
# Vérifier que tous les endpoints social apparaissent :
# POST /players/register
# GET/PATCH /players/me
# POST /players/me/photo
# GET /players/{username}
# POST /matches
# GET /matches/me
# POST /matches/{id}/vote
# GET /rankings
# GET /rankings/me
# GET /feed
# POST /feed/{id}/like
```

- [ ] **Step 5 : Commit**

```bash
git add backend/routers/social/rankings.py backend/routers/social/feed.py backend/main.py
git commit -m "feat(social): routers rankings (locaux + percentile) et feed social"
```

---

## Task 8 — Frontend: types + auth + social API client

**Files:**
- Create: `frontend/src/lib/social-types.ts`
- Create: `frontend/src/lib/social-api.ts`
- Create: `frontend/src/lib/auth.ts`

- [ ] **Step 1 : Créer `frontend/src/lib/social-types.ts`**

```typescript
export type Tier = "silver" | "gold" | "elite" | "legend"

export interface SocialPlayer {
  id: string
  name: string
  username: string
  position: string | null
  position_short: string | null
  club: string | null
  region: string | null
  category: string | null
  country_code: string | null
  photo_url: string | null
  machine_score: number
  machine_score_tier: Tier
  data_level: 1 | 2 | 3
}

export interface MatchLog {
  id: string
  opponent_name: string
  home_score: number | null
  away_score: number | null
  match_date: string
  competition: string | null
  is_home: boolean
}

export interface FeedPost {
  id: string
  post_type: string
  content: Record<string, unknown> | null
  likes_count: number
  created_at: string
  player_name: string
  player_username: string
  player_photo_url: string | null
  player_score: number
  player_tier: Tier
}

export interface RankingRow {
  rank: number
  percentile: number
  player_id: string
  name: string
  username: string
  position_short: string | null
  club: string | null
  machine_score: number
  machine_score_tier: Tier
  photo_url: string | null
}

export interface PlayerRanking {
  rank: number
  percentile: number
  total_players: number
  position: string | null
  region: string | null
  category: string | null
}

export interface VoteRequest {
  voted_for_id: string
  is_votm: boolean
  badges: string[]
}
```

- [ ] **Step 2 : Installer Supabase client dans frontend**

```bash
cd frontend && npm install @supabase/supabase-js
```

- [ ] **Step 3 : Créer `frontend/src/lib/auth.ts`**

```typescript
import { createClient } from "@supabase/supabase-js"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export async function getToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

export async function signUp(email: string, password: string) {
  return supabase.auth.signUp({ email, password })
}

export async function signIn(email: string, password: string) {
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signOut() {
  return supabase.auth.signOut()
}
```

- [ ] **Step 4 : Créer `frontend/src/lib/social-api.ts`**

```typescript
import { getToken } from "./auth"
import type {
  SocialPlayer, MatchLog, FeedPost, RankingRow, PlayerRanking, VoteRequest
} from "./social-types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function authFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getToken()
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `API ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const socialApi = {
  register: (body: {
    name: string; username: string; position?: string
    club?: string; region?: string; category?: string; country_code?: string
  }): Promise<SocialPlayer> =>
    authFetch("/players/register", { method: "POST", body: JSON.stringify(body) }),

  me: (): Promise<SocialPlayer> =>
    authFetch("/players/me"),

  updateMe: (body: Partial<SocialPlayer>): Promise<SocialPlayer> =>
    authFetch("/players/me", { method: "PATCH", body: JSON.stringify(body) }),

  uploadPhoto: async (file: File): Promise<SocialPlayer> => {
    const token = await getToken()
    const form = new FormData()
    form.append("file", file)
    const res = await fetch(`${BASE}/players/me/photo`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    })
    if (!res.ok) throw new Error("Upload photo échoué")
    return res.json()
  },

  getPlayer: (username: string): Promise<SocialPlayer> =>
    authFetch(`/players/${username}`),

  createMatch: (body: {
    opponent_name: string; home_score?: number; away_score?: number
    match_date: string; competition?: string; is_home?: boolean
    team_id?: string; players?: object[]
  }): Promise<MatchLog> =>
    authFetch("/matches", { method: "POST", body: JSON.stringify(body) }),

  myMatches: (): Promise<MatchLog[]> =>
    authFetch("/matches/me"),

  vote: (matchId: string, body: VoteRequest): Promise<{ status: string }> =>
    authFetch(`/matches/${matchId}/vote`, { method: "POST", body: JSON.stringify(body) }),

  feed: (offset = 0): Promise<FeedPost[]> =>
    authFetch(`/feed?offset=${offset}`),

  likePost: (postId: string): Promise<void> =>
    authFetch(`/feed/${postId}/like`, { method: "POST" }),

  myRanking: (): Promise<PlayerRanking | null> =>
    authFetch("/rankings/me"),

  rankings: (params: {
    region?: string; category?: string; position?: string; limit?: number
  }): Promise<RankingRow[]> => {
    const q = new URLSearchParams()
    if (params.region) q.set("region", params.region)
    if (params.category) q.set("category", params.category)
    if (params.position) q.set("position", params.position)
    if (params.limit) q.set("limit", String(params.limit))
    return authFetch(`/rankings?${q}`)
  },
}
```

- [ ] **Step 5 : Ajouter les env vars dans `frontend/.env.local`**

```bash
echo 'NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...' >> frontend/.env.local
```

- [ ] **Step 6 : Commit**

```bash
git add frontend/src/lib/social-types.ts frontend/src/lib/social-api.ts frontend/src/lib/auth.ts frontend/
git commit -m "feat(frontend): types social + client API auth Supabase"
```

---

## Task 9 — Player Card FUT (composant React)

**Files:**
- Create: `frontend/src/components/player-card/PlayerCardTiers.ts`
- Create: `frontend/src/components/player-card/PlayerCard.tsx`
- Create: `frontend/src/components/player-card/PhotoUpload.tsx`

- [ ] **Step 1 : Créer `frontend/src/components/player-card/PlayerCardTiers.ts`**

```typescript
import type { Tier } from "@/lib/social-types"

export interface TierConfig {
  bgGradient: string
  accentColor: string
  borderColor: string
  shadowColor: string
  scoreColor: string
  fadeTo: string
}

export const TIER_CONFIG: Record<Tier, TierConfig> = {
  silver: {
    bgGradient: "linear-gradient(160deg, #1a1a1a 0%, #2d2d2d 40%, #111 100%)",
    accentColor: "rgba(180,180,200,0.4)",
    borderColor: "rgba(180,180,200,0.35)",
    shadowColor: "rgba(0,0,0,0.4)",
    scoreColor: "#C8C8D8",
    fadeTo: "#111",
  },
  gold: {
    bgGradient: "linear-gradient(160deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%)",
    accentColor: "rgba(255,200,60,0.6)",
    borderColor: "rgba(255,200,60,0.5)",
    shadowColor: "rgba(255,180,30,0.3)",
    scoreColor: "#FFE566",
    fadeTo: "#16213e",
  },
  elite: {
    bgGradient: "linear-gradient(160deg, #2d1515 0%, #4a1010 40%, #1a0505 100%)",
    accentColor: "rgba(220,60,60,0.7)",
    borderColor: "rgba(220,60,60,0.6)",
    shadowColor: "rgba(255,60,60,0.35)",
    scoreColor: "#FF8080",
    fadeTo: "#1a0505",
  },
  legend: {
    bgGradient: "linear-gradient(160deg, #1a0d2e 0%, #2d1a4a 40%, #0d0d1a 100%)",
    accentColor: "rgba(180,100,255,0.6)",
    borderColor: "rgba(180,100,255,0.55)",
    shadowColor: "rgba(160,80,255,0.4)",
    scoreColor: "#D080FF",
    fadeTo: "#0d0d1a",
  },
}
```

- [ ] **Step 2 : Créer `frontend/src/components/player-card/PlayerCard.tsx`**

```tsx
"use client"
import { TIER_CONFIG } from "./PlayerCardTiers"
import type { Tier } from "@/lib/social-types"

export interface PlayerCardAttributes {
  tec: number; phy: number; vit: number
  def: number; vis: number; imp: number
}

interface Props {
  score: number
  tier: Tier
  positionShort: string
  name: string
  photoUrl?: string | null
  countryCode?: string | null
  clubEmoji?: string
  attributes: PlayerCardAttributes
  size?: "sm" | "md" | "lg"
  onPhotoClick?: () => void
  className?: string
}

const SIZES = {
  sm: { width: 140, height: 200, scoreSize: "1.6rem", nameSize: "0.65rem", statSize: "0.52rem" },
  md: { width: 200, height: 290, scoreSize: "2.4rem", nameSize: "0.9rem", statSize: "0.7rem" },
  lg: { width: 280, height: 406, scoreSize: "3.2rem", nameSize: "1.2rem", statSize: "0.9rem" },
}

const FLAG_MAP: Record<string, string> = {
  MQ: "🇲🇶", FR: "🇫🇷", BR: "🇧🇷", NG: "🇳🇬", CM: "🇨🇲",
  SN: "🇸🇳", CI: "🇨🇮", MA: "🇲🇦", DZ: "🇩🇿", ES: "🇪🇸",
  PT: "🇵🇹", GB: "🇬🇧", DE: "🇩🇪", IT: "🇮🇹", AR: "🇦🇷",
}

export default function PlayerCard({
  score, tier, positionShort, name, photoUrl, countryCode,
  clubEmoji = "⚽", attributes, size = "md", onPhotoClick, className,
}: Props) {
  const cfg = TIER_CONFIG[tier]
  const sz = SIZES[size]
  const flag = countryCode ? (FLAG_MAP[countryCode.toUpperCase()] ?? "🌍") : "🌍"
  const attrs = [
    { val: attributes.tec, lbl: "TEC" },
    { val: attributes.phy, lbl: "PHY" },
    { val: attributes.vit, lbl: "VIT" },
    { val: attributes.def, lbl: "DEF" },
    { val: attributes.vis, lbl: "VIS" },
    { val: attributes.imp, lbl: "IMP" },
  ]

  return (
    <div
      className={className}
      style={{
        width: sz.width, height: sz.height,
        background: cfg.bgGradient,
        borderRadius: 14,
        border: `1.5px solid ${cfg.borderColor}`,
        boxShadow: `0 12px 40px ${cfg.shadowColor}, 0 0 0 1px ${cfg.accentColor}22`,
        position: "relative", overflow: "hidden",
        display: "flex", flexDirection: "column",
        fontFamily: "'Outfit', sans-serif",
        cursor: onPhotoClick && !photoUrl ? "pointer" : "default",
      }}
    >
      {/* Top row: score + flags */}
      <div style={{ display: "flex", alignItems: "flex-start", padding: "10px 10px 0", gap: 6 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <span style={{
            fontFamily: "'Oswald', 'Outfit', sans-serif",
            fontSize: sz.scoreSize, fontWeight: 700, lineHeight: 1,
            color: cfg.scoreColor,
            textShadow: `0 2px 8px ${cfg.shadowColor}`,
          }}>{score}</span>
          <span style={{
            fontSize: `calc(${sz.statSize} * 1.1)`, fontWeight: 800,
            color: cfg.scoreColor, opacity: 0.85, letterSpacing: "0.1em",
            textTransform: "uppercase", marginTop: 1,
          }}>{positionShort}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 2 }}>
          <span style={{ fontSize: size === "sm" ? "0.75rem" : "0.9rem" }}>{flag}</span>
          <span style={{ fontSize: size === "sm" ? "0.7rem" : "0.85rem" }}>{clubEmoji}</span>
        </div>
      </div>

      {/* Photo area */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {photoUrl ? (
          <img
            src={photoUrl} alt={name}
            style={{
              width: "100%", height: "100%",
              objectFit: "cover", objectPosition: "top center",
              filter: `drop-shadow(0 -4px 12px ${cfg.shadowColor})`,
            }}
          />
        ) : (
          <div
            onClick={onPhotoClick}
            style={{
              width: "100%", height: "100%",
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              gap: 6, cursor: onPhotoClick ? "pointer" : "default",
            }}
          >
            <div style={{
              width: size === "sm" ? 44 : 60, height: size === "sm" ? 44 : 60,
              borderRadius: "50%", border: `2px dashed ${cfg.accentColor}`,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", gap: 4,
            }}>
              <span style={{ fontSize: size === "sm" ? "1rem" : "1.4rem", opacity: 0.5 }}>📷</span>
            </div>
            {size !== "sm" && (
              <span style={{
                fontSize: "0.6rem", color: "rgba(255,255,255,0.35)",
                textAlign: "center", fontWeight: 600, lineHeight: 1.3,
              }}>Ajouter ma photo</span>
            )}
          </div>
        )}
        {/* Gradient fade */}
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 0, height: "60%",
          background: `linear-gradient(transparent, ${cfg.fadeTo} 90%)`,
          pointerEvents: "none",
        }} />
      </div>

      {/* Name */}
      <div style={{
        fontFamily: "'Oswald', 'Outfit', sans-serif",
        fontSize: sz.nameSize, fontWeight: 700,
        textAlign: "center", padding: "0 8px",
        textTransform: "uppercase", letterSpacing: "0.08em",
        color: "#fff", textShadow: "0 2px 6px rgba(0,0,0,0.8)",
        position: "relative", zIndex: 2, marginTop: -4,
        whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
      }}>{name.split(" ").map((w, i) => i === 0 ? w[0] + "." : w).join(" ")}</div>

      {/* Divider */}
      <div style={{
        height: 1, margin: `4px ${size === "sm" ? 8 : 12}px`,
        background: cfg.accentColor, opacity: 0.5,
      }} />

      {/* Stats 3x2 */}
      <div style={{
        display: "grid", gridTemplateColumns: "1fr 1fr 1fr",
        padding: `0 ${size === "sm" ? 6 : 10}px ${size === "sm" ? 8 : 12}px`,
      }}>
        {attrs.map(({ val, lbl }) => (
          <div key={lbl} style={{ textAlign: "center", padding: "2px 0" }}>
            <div style={{
              fontFamily: "'Oswald', monospace", fontSize: sz.statSize,
              fontWeight: 600, color: "rgba(255,255,255,0.9)",
            }}>{val}</div>
            <div style={{
              fontSize: `calc(${sz.statSize} * 0.75)`,
              color: cfg.scoreColor, opacity: 0.7,
              textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700,
            }}>{lbl}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3 : Créer `frontend/src/components/player-card/PhotoUpload.tsx`**

```tsx
"use client"
import { useRef, useState } from "react"

interface Props {
  onFile: (file: File) => void
  onClose: () => void
}

export default function PhotoUpload({ onFile, onClose }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setSelectedFile(file)
    const url = URL.createObjectURL(file)
    setPreview(url)
  }

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)",
      display: "flex", alignItems: "flex-end", zIndex: 1000,
    }} onClick={onClose}>
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: "100%", background: "#17182A",
          borderRadius: "28px 28px 0 0", padding: "12px 20px 40px",
          border: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <div style={{
          width: 36, height: 4, background: "rgba(255,255,255,0.15)",
          borderRadius: 2, margin: "0 auto 20px",
        }} />
        <h3 style={{ color: "#F2F4FF", fontWeight: 800, marginBottom: 8 }}>
          Ajoute ta photo de joueur
        </h3>
        <p style={{ color: "#7B8098", fontSize: "0.8rem", marginBottom: 20, lineHeight: 1.5 }}>
          Ta photo apparaîtra sur ta Player Card. Utilise une photo de face, bien éclairée.
        </p>

        {preview && (
          <div style={{ textAlign: "center", marginBottom: 16 }}>
            <img src={preview} alt="preview" style={{
              width: 120, height: 160, objectFit: "cover",
              borderRadius: 12, border: "2px solid rgba(200,255,87,0.3)",
            }} />
          </div>
        )}

        <input
          ref={inputRef} type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleChange}
          style={{ display: "none" }}
        />

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <button
            onClick={() => inputRef.current?.click()}
            style={{
              width: "100%", background: "#C8FF57", color: "#0E0F18",
              border: "none", borderRadius: 100, padding: "14px",
              fontWeight: 800, fontSize: "0.9rem", cursor: "pointer",
              fontFamily: "'Outfit', sans-serif",
            }}
          >
            {preview ? "Changer la photo" : "📷 Choisir une photo"}
          </button>

          {selectedFile && (
            <button
              onClick={() => { onFile(selectedFile); onClose() }}
              style={{
                width: "100%", background: "rgba(200,255,87,0.15)",
                color: "#C8FF57", border: "1px solid rgba(200,255,87,0.3)",
                borderRadius: 100, padding: "14px",
                fontWeight: 800, fontSize: "0.9rem", cursor: "pointer",
                fontFamily: "'Outfit', sans-serif",
              }}
            >
              Confirmer et enregistrer
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4 : Commit**

```bash
git add frontend/src/components/player-card/
git commit -m "feat(frontend): Player Card FUT-style (tiers silver/gold/elite/legend) + photo upload bottom sheet"
```

---

## Task 10 — Pages sociales frontend

**Files:**
- Create: `frontend/src/app/(social)/layout.tsx`
- Create: `frontend/src/app/(social)/profil/page.tsx`
- Create: `frontend/src/app/(social)/feed/page.tsx`
- Create: `frontend/src/app/(social)/match/new/page.tsx`
- Create: `frontend/src/app/(social)/classements/page.tsx`

- [ ] **Step 1 : Créer `frontend/src/app/(social)/layout.tsx`**

```tsx
"use client"
import { usePathname, useRouter } from "next/navigation"

const NAV = [
  { href: "/feed",        icon: "🏠", label: "Feed" },
  { href: "/profil",      icon: "👤", label: "Profil" },
  { href: "/match/new",   icon: "+",  label: "",     isAdd: true },
  { href: "/classements", icon: "🏆", label: "Clsmt" },
  { href: "/equipe",      icon: "⚽", label: "Équipe" },
]

export default function SocialLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname()
  return (
    <div style={{
      maxWidth: 480, margin: "0 auto", minHeight: "100dvh",
      background: "#0E0F18", display: "flex", flexDirection: "column",
      position: "relative",
    }}>
      <div style={{ flex: 1, overflowY: "auto", paddingBottom: 80 }}>
        {children}
      </div>
      <nav style={{
        position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)",
        width: "100%", maxWidth: 480,
        height: 72, background: "rgba(14,15,24,0.96)",
        backdropFilter: "blur(20px)",
        borderTop: "1px solid rgba(255,255,255,0.05)",
        display: "flex", alignItems: "flex-start", justifyContent: "space-around",
        paddingTop: 10, zIndex: 100,
      }}>
        {NAV.map(({ href, icon, label, isAdd }) => {
          const active = path.startsWith(href) && href !== "/match/new"
          if (isAdd) return (
            <a key={href} href={href} style={{
              width: 52, height: 44, background: "#C8FF57",
              borderRadius: 100, display: "flex",
              alignItems: "center", justifyContent: "center",
              fontSize: "1.5rem", color: "#0E0F18", fontWeight: 900,
              marginTop: -12, boxShadow: "0 4px 20px rgba(200,255,87,0.35)",
              textDecoration: "none",
            }}>+</a>
          )
          return (
            <a key={href} href={href} style={{
              display: "flex", flexDirection: "column", alignItems: "center", gap: 3,
              textDecoration: "none",
              color: active ? "#C8FF57" : "#7B8098",
              fontSize: "0.55rem", fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.07em",
            }}>
              <span style={{ fontSize: "1.1rem" }}>{icon}</span>
              <span>{label}</span>
            </a>
          )
        })}
      </nav>
    </div>
  )
}
```

- [ ] **Step 2 : Créer `frontend/src/app/(social)/feed/page.tsx`**

```tsx
"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import type { FeedPost } from "@/lib/social-types"

const POST_TYPE_LABEL: Record<string, string> = {
  match_added: "a ajouté un match",
  votm: "a été élu joueur du match",
  card_upgrade: "a upgradé sa Player Card",
  ranking_change: "a changé de classement",
}

export default function FeedPage() {
  const [posts, setPosts] = useState<FeedPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    socialApi.feed().then(setPosts).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60 }}>
      <div style={{ fontSize: "2rem", marginBottom: 12 }}>⚽</div>
      Chargement du feed...
    </div>
  )

  return (
    <div style={{ padding: "16px 0 0" }}>
      <div style={{ padding: "0 16px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF", letterSpacing: "-0.02em" }}>
            Orbyon Sport
          </div>
          <div style={{ fontSize: "0.72rem", color: "#7B8098", fontWeight: 600 }}>
            Activité de ta communauté
          </div>
        </div>
        <div style={{ fontSize: "1.2rem" }}>🔔</div>
      </div>

      {posts.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7B8098" }}>
          <div style={{ fontSize: "3rem", marginBottom: 12 }}>🏟️</div>
          <p style={{ fontSize: "0.88rem" }}>Aucune activité pour l&apos;instant.<br />Ajoute ton premier match !</p>
        </div>
      ) : posts.map(post => (
        <div key={post.id} style={{
          margin: "0 16px 10px",
          background: "#17182A",
          borderRadius: 18, padding: 14,
          border: "1px solid rgba(255,255,255,0.05)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <div style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "linear-gradient(135deg,#252840,#151628)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.9rem", border: "1.5px solid rgba(200,255,87,0.15)",
              flexShrink: 0,
            }}>
              {post.player_photo_url
                ? <img src={post.player_photo_url} alt="" style={{ width: "100%", height: "100%", borderRadius: "50%", objectFit: "cover" }} />
                : "⚽"}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "0.82rem", fontWeight: 800, color: "#F2F4FF" }}>
                {post.player_name}
              </div>
              <div style={{ fontSize: "0.65rem", color: "#7B8098", marginTop: 1 }}>
                {POST_TYPE_LABEL[post.post_type] ?? post.post_type}
              </div>
            </div>
            <div style={{ fontSize: "0.62rem", color: "#3D4060" }}>
              {new Date(post.created_at).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" })}
            </div>
          </div>
          {post.content && post.post_type === "match_added" && (
            <div style={{
              background: "rgba(200,255,87,0.06)", borderRadius: 10,
              padding: "8px 12px", fontSize: "0.8rem", color: "#b0b8cc",
              border: "1px solid rgba(200,255,87,0.1)",
            }}>
              ⚽ vs <strong style={{ color: "#F2F4FF" }}>{String(post.content.opponent)}</strong>
              {post.content.score ? ` — ${post.content.score}` : ""}
            </div>
          )}
          <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
            <button
              onClick={() => socialApi.likePost(post.id).catch(console.error)}
              style={{
                fontSize: "0.72rem", color: "#7B8098",
                background: "rgba(255,255,255,0.04)", border: "none",
                borderRadius: 100, padding: "5px 12px", cursor: "pointer",
                fontFamily: "'Outfit', sans-serif", fontWeight: 600,
              }}
            >
              Réagir {post.likes_count > 0 ? post.likes_count : ""}
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 3 : Créer `frontend/src/app/(social)/profil/page.tsx`**

```tsx
"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import PlayerCard from "@/components/player-card/PlayerCard"
import PhotoUpload from "@/components/player-card/PhotoUpload"
import type { SocialPlayer } from "@/lib/social-types"

export default function ProfilPage() {
  const [player, setPlayer] = useState<SocialPlayer | null>(null)
  const [showPhotoUpload, setShowPhotoUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    socialApi.me().then(setPlayer).catch(console.error).finally(() => setLoading(false))
  }, [])

  async function handlePhotoFile(file: File) {
    setUploading(true)
    try {
      const updated = await socialApi.uploadPhoto(file)
      setPlayer(updated)
    } catch (e) { console.error(e) }
    setUploading(false)
  }

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60 }}>
      Chargement...
    </div>
  )

  if (!player) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60 }}>
      <p>Non connecté. <a href="/auth/login" style={{ color: "#C8FF57" }}>Se connecter</a></p>
    </div>
  )

  const attrs = { tec: 60, phy: 60, vit: 60, def: 60, vis: 60, imp: player.machine_score }

  return (
    <div style={{ padding: "16px 16px 0" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF" }}>Mon Profil</div>
          <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>@{player.username}</div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button style={{
            background: "#17182A", border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "50%", width: 36, height: 36, fontSize: "0.9rem",
            color: "#7B8098", cursor: "pointer",
          }}>⚙️</button>
        </div>
      </div>

      {/* Player Card */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
        <PlayerCard
          score={player.machine_score}
          tier={player.machine_score_tier}
          positionShort={player.position_short ?? "?"}
          name={player.name}
          photoUrl={player.photo_url}
          countryCode={player.country_code ?? undefined}
          attributes={attrs}
          size="lg"
          onPhotoClick={() => setShowPhotoUpload(true)}
        />
      </div>

      {/* Score mise à jour CTA si pas de photo */}
      {!player.photo_url && (
        <div style={{
          background: "rgba(200,255,87,0.06)", borderRadius: 14,
          padding: "12px 16px", marginBottom: 16,
          border: "1px solid rgba(200,255,87,0.15)",
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <span style={{ fontSize: "1.2rem" }}>📷</span>
          <div style={{ flex: 1, fontSize: "0.82rem", color: "#b0b8cc" }}>
            Ajoute ta photo pour activer ta Player Card
          </div>
          <button
            onClick={() => setShowPhotoUpload(true)}
            style={{
              background: "#C8FF57", color: "#0E0F18", border: "none",
              borderRadius: 100, padding: "6px 14px", fontWeight: 800,
              fontSize: "0.72rem", cursor: "pointer", fontFamily: "'Outfit'",
            }}
          >+ Photo</button>
        </div>
      )}

      {/* Stats bar */}
      <div style={{
        display: "flex", background: "#17182A", borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.05)", marginBottom: 16, overflow: "hidden",
      }}>
        {[
          { val: player.machine_score, lbl: "Score" },
          { val: "—", lbl: "Matchs" },
          { val: "—", lbl: "Buts" },
          { val: "—", lbl: "Note" },
        ].map(({ val, lbl }, i) => (
          <div key={lbl} style={{
            flex: 1, padding: "12px 8px", textAlign: "center",
            borderLeft: i > 0 ? "1px solid rgba(255,255,255,0.05)" : "none",
          }}>
            <div style={{
              fontSize: "1.2rem", fontWeight: 800, color: "#F2F4FF",
              fontFamily: "'JetBrains Mono', monospace",
            }}>{val}</div>
            <div style={{
              fontSize: "0.52rem", color: "#7B8098",
              textTransform: "uppercase", letterSpacing: "0.1em",
              marginTop: 3, fontWeight: 700,
            }}>{lbl}</div>
          </div>
        ))}
      </div>

      {/* Partage */}
      <button style={{
        width: "100%", background: "transparent",
        border: "1.5px solid rgba(200,255,87,0.3)", color: "#C8FF57",
        borderRadius: 100, padding: 12, fontWeight: 800,
        fontSize: "0.82rem", cursor: "pointer", fontFamily: "'Outfit'",
      }}>
        🔗 Partager mon profil
      </button>

      {showPhotoUpload && (
        <PhotoUpload
          onFile={handlePhotoFile}
          onClose={() => setShowPhotoUpload(false)}
        />
      )}
      {uploading && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 999, color: "#C8FF57", fontSize: "0.9rem", fontWeight: 700,
        }}>
          Upload en cours...
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4 : Créer `frontend/src/app/(social)/match/new/page.tsx`**

```tsx
"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { socialApi } from "@/lib/social-api"

export default function NewMatchPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    opponent_name: "", home_score: "", away_score: "",
    match_date: new Date().toISOString().slice(0, 10),
    competition: "", is_home: true,
    goals: "0", assists: "0", shots: "0", key_passes: "0",
    player_rating: "7",
  })
  const [loading, setLoading] = useState(false)

  const inp = (field: string, type: "text" | "number" = "text") => ({
    value: form[field as keyof typeof form] as string,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm(f => ({ ...f, [field]: e.target.value })),
    type,
    style: {
      width: "100%", background: "#17182A", color: "#F2F4FF",
      border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12,
      padding: "12px 14px", fontSize: "0.85rem", outline: "none",
      fontFamily: "'Outfit', sans-serif",
    },
  })

  async function submit() {
    if (!form.opponent_name || !form.match_date) return
    setLoading(true)
    try {
      await socialApi.createMatch({
        opponent_name: form.opponent_name,
        home_score: form.home_score ? Number(form.home_score) : undefined,
        away_score: form.away_score ? Number(form.away_score) : undefined,
        match_date: form.match_date,
        competition: form.competition || undefined,
        is_home: form.is_home,
        players: [{
          player_id: "me", // backend remplace par le player courant
          goals: Number(form.goals),
          assists: Number(form.assists),
          shots: Number(form.shots),
          key_passes: Number(form.key_passes),
          player_rating: Number(form.player_rating),
        }],
      })
      router.push("/profil")
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const label = (text: string) => (
    <div style={{ fontSize: "0.68rem", color: "#7B8098", fontWeight: 700,
      textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 6 }}>
      {text}
    </div>
  )

  return (
    <div style={{ padding: "20px 16px" }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: "1.2rem", fontWeight: 900, color: "#F2F4FF" }}>Ajouter un match</div>
        <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>Enrichis ton profil avec tes performances</div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          {label("Adversaire *")}
          <input {...inp("opponent_name")} placeholder="Nom de l'équipe adverse" />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>{label("Score (nous)")} <input {...inp("home_score", "number")} placeholder="2" /></div>
          <div>{label("Score (eux)")} <input {...inp("away_score", "number")} placeholder="1" /></div>
        </div>

        <div>{label("Date *")} <input {...inp("match_date")} type="date" /></div>

        <div>{label("Compétition")} <input {...inp("competition")} placeholder="Ligue Martinique J12" /></div>

        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 16 }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#F2F4FF", marginBottom: 14 }}>
            Mes stats
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>{label("Buts")} <input {...inp("goals", "number")} /></div>
            <div>{label("Passes déc.")} <input {...inp("assists", "number")} /></div>
            <div>{label("Tirs")} <input {...inp("shots", "number")} /></div>
            <div>{label("Passes clés")} <input {...inp("key_passes", "number")} /></div>
          </div>
          <div style={{ marginTop: 12 }}>
            {label(`Ma note : ${form.player_rating}/10`)}
            <input type="range" min="1" max="10" step="0.5"
              value={form.player_rating}
              onChange={e => setForm(f => ({ ...f, player_rating: e.target.value }))}
              style={{ width: "100%", accentColor: "#C8FF57" }}
            />
          </div>
        </div>

        <button onClick={submit} disabled={loading} style={{
          width: "100%", background: loading ? "rgba(200,255,87,0.3)" : "#C8FF57",
          color: "#0E0F18", border: "none", borderRadius: 100,
          padding: 14, fontWeight: 800, fontSize: "0.9rem",
          cursor: loading ? "not-allowed" : "pointer",
          fontFamily: "'Outfit', sans-serif",
        }}>
          {loading ? "Enregistrement..." : "⚽ Enregistrer le match"}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 5 : Créer `frontend/src/app/(social)/classements/page.tsx`**

```tsx
"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import type { RankingRow, PlayerRanking } from "@/lib/social-types"

const TIER_COLORS = { silver: "#C8C8D8", gold: "#FFE566", elite: "#FF8080", legend: "#D080FF" }

export default function ClassementsPage() {
  const [rows, setRows] = useState<RankingRow[]>([])
  const [myRanking, setMyRanking] = useState<PlayerRanking | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      socialApi.rankings({ limit: 50 }).then(setRows),
      socialApi.myRanking().then(setMyRanking),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60 }}>Chargement...</div>
  )

  return (
    <div style={{ padding: "16px 0 0" }}>
      <div style={{ padding: "0 16px 16px" }}>
        <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF" }}>Classements</div>
        <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>Classement local par poste et région</div>
      </div>

      {myRanking && (
        <div style={{
          margin: "0 16px 16px",
          background: "linear-gradient(135deg,#0d1020,#131428)",
          borderRadius: 16, padding: 16,
          border: "1px solid rgba(68,136,255,0.2)",
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <div>
            <div style={{ fontSize: "2.2rem", fontWeight: 900, color: "#FFD60A", lineHeight: 1 }}>
              #{myRanking.rank}
            </div>
            <div style={{ fontSize: "0.72rem", color: "#b0b8cc", marginTop: 4 }}>
              {myRanking.position} · {myRanking.region}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: "0.65rem", color: "#7B8098", marginBottom: 5 }}>
              Top {100 - Math.round(myRanking.percentile)}% · {myRanking.total_players} joueurs
            </div>
            <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3, overflow: "hidden" }}>
              <div style={{
                height: "100%", width: `${myRanking.percentile}%`,
                background: "linear-gradient(90deg,#FFD60A,#FF9800)", borderRadius: 3,
              }} />
            </div>
          </div>
        </div>
      )}

      {rows.map(row => (
        <div key={row.player_id} style={{
          margin: "0 16px 4px",
          background: "#17182A", borderRadius: 12, padding: "10px 14px",
          display: "flex", alignItems: "center", gap: 10,
          border: "1px solid rgba(255,255,255,0.04)",
        }}>
          <div style={{
            width: 24, textAlign: "center",
            fontSize: "0.8rem", fontWeight: 700,
            color: row.rank <= 3 ? "#FFD60A" : "#7B8098",
          }}>{row.rank}</div>
          <div style={{
            width: 34, height: 34, borderRadius: "50%",
            background: "linear-gradient(135deg,#1a2030,#0d1020)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "0.9rem", border: "1.5px solid rgba(255,255,255,0.07)",
            flexShrink: 0, overflow: "hidden",
          }}>
            {row.photo_url
              ? <img src={row.photo_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              : "⚽"}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#F2F4FF" }}>{row.name}</div>
            <div style={{ fontSize: "0.62rem", color: "#7B8098", marginTop: 1 }}>
              {row.position_short} · {row.club ?? "—"}
            </div>
          </div>
          <div style={{
            fontSize: "1rem", fontWeight: 800,
            color: TIER_COLORS[row.machine_score_tier] ?? "#F2F4FF",
          }}>{row.machine_score}</div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 6 : Vérifier le build**

```bash
cd frontend && npm run build 2>&1 | tail -20
# Attendu : ✓ Compiled successfully
```

- [ ] **Step 7 : Commit final Phase 1**

```bash
cd C:/Users/jimmy/sportanalytics
git add frontend/src/app/ frontend/src/components/ frontend/src/lib/
git commit -m "feat(frontend): pages sociales - Feed, Profil + Player Card FUT, Nouveau match, Classements"
git push origin feature/saas-migration
```

---

## Résumé — Effort Phase 1

| Task | Durée estimée |
|------|--------------|
| 1 — PostgreSQL + SQLAlchemy | 30 min |
| 2 — Auth Supabase | 15 min |
| 3 — Router profiles | 20 min |
| 4 — Upload photo | 15 min |
| 5 — Matches + Votes | 25 min |
| 6 — Machine Score L1 | 20 min |
| 7 — Rankings + Feed | 20 min |
| 8 — Types + API client | 15 min |
| 9 — Player Card FUT | 30 min |
| 10 — Pages sociales | 45 min |
| **Total** | **~3h30** |

## Variables d'environnement requises

Créer un projet Supabase gratuit sur [supabase.com](https://supabase.com), récupérer :
- `SUPABASE_URL` → Settings → API → Project URL
- `SUPABASE_ANON_KEY` → Settings → API → anon key
- `SUPABASE_JWT_SECRET` → Settings → API → JWT Secret

Pour le stockage photos : créer un bucket "orbyon-photos" dans Supabase Storage (public).
