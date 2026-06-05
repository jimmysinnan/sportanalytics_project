from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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


@router.get("/me", response_model=RankingOut | None)
async def get_my_ranking(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Get the current player's ranking (latest computed)."""
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
    """Local rankings computed on-the-fly from Player.machine_score."""
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
