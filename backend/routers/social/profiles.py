from __future__ import annotations
import os, uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import Player
from auth import get_current_player

router = APIRouter(prefix="/players", tags=["social-players"])

POSITION_SHORT_MAP = {
    "Gardien": "GB", "Défenseur Central": "DC", "Latéral Droit": "LD",
    "Latéral Gauche": "LG", "Milieu Défensif": "MD", "Milieu Central": "MC",
    "Milieu Offensif": "MO", "Ailier Droit": "AD", "Ailier Gauche": "AG",
    "Attaquant": "BU", "Avant-Centre": "AC",
}


def score_to_tier(score: int) -> str:
    if score >= 95:
        return "legend"
    if score >= 85:
        return "elite"
    if score >= 75:
        return "gold"
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
        payload = _jwt.decode(
            token,
            os.environ.get("SUPABASE_JWT_SECRET", ""),
            algorithms=["HS256"],
            audience="authenticated",
        )
        auth_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "Token invalide")

    existing = await db.execute(select(Player).where(Player.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Ce username est déjà pris")

    pos_short = POSITION_SHORT_MAP.get(body.position or "", "") or None
    player = Player(
        auth_id=auth_id,
        name=body.name,
        username=body.username,
        position=body.position,
        position_short=pos_short,
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
async def get_my_profile(player: Player = Depends(get_current_player)):
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
async def get_player_by_username(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player).where(Player.username == username))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(404, "Joueur introuvable")
    return player


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
