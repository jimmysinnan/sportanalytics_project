from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import MatchLog, MatchPlayer, Player, FeedPost
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
