from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import PeerVote, MatchLog, MatchPlayer, Player, PlayerBadge, FeedPost
from auth import get_current_player
from services.machine_score import recompute_machine_score

router = APIRouter(prefix="/matches", tags=["social-votes"])

VALID_BADGES = {
    "rapide", "solide", "technique", "décisif", "collectif",
    "vision", "muraille", "clutch", "leader", "régulier",
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
    match = await db.get(MatchLog, match_id)
    if not match:
        raise HTTPException(404, "Match introuvable")

    voter_in_match = await db.execute(
        select(MatchPlayer).where(
            MatchPlayer.match_id == match_id,
            MatchPlayer.player_id == voter.id,
        )
    )
    if not voter_in_match.scalar_one_or_none():
        raise HTTPException(403, "Tu n'as pas participé à ce match")

    if body.voted_for_id == voter.id:
        raise HTTPException(400, "Tu ne peux pas voter pour toi-même")

    existing = await db.execute(
        select(PeerVote).where(
            PeerVote.match_id == match_id,
            PeerVote.voter_id == voter.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Tu as déjà voté pour ce match")

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

    for badge_key in body.badges:
        db.add(PlayerBadge(
            player_id=body.voted_for_id,
            badge_key=badge_key,
            badge_label=badge_key.capitalize(),
            source_type="peer_vote",
        ))

    if body.is_votm:
        db.add(FeedPost(
            player_id=body.voted_for_id,
            post_type="votm",
            content={"match_id": match_id, "voter_id": voter.id},
        ))

    await db.commit()
    await recompute_machine_score(body.voted_for_id, db)
    return {"status": "vote enregistré"}
