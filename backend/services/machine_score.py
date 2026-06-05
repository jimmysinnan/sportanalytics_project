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


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


async def recompute_machine_score(player_id: str, db: AsyncSession) -> int:
    """
    Calcule et sauvegarde le Machine Score Level 1.
    Formule : social 35% + stats 25% + regularite 25% + progression 15%
    """
    # Composante sociale
    votes_row = await db.execute(
        select(
            func.count(PeerVote.id),
            func.sum(PeerVote.is_votm.cast(int)),
        ).where(PeerVote.voted_for_id == player_id)
    )
    total_votes, total_votm = votes_row.one()
    total_votes = int(total_votes or 0)
    total_votm = int(total_votm or 0)

    badges_count = await db.scalar(
        select(func.count(PlayerBadge.id)).where(PlayerBadge.player_id == player_id)
    ) or 0

    vote_comp = _clamp(total_votes / 20 * 60)
    votm_comp = _clamp(total_votm * 10, hi=25.0)
    badge_comp = _clamp(badges_count * 3, hi=15.0)
    social_score = _clamp(vote_comp + votm_comp + badge_comp)

    # Composante stats
    stats_row = await db.execute(
        select(
            func.coalesce(func.sum(MatchPlayer.goals), 0),
            func.coalesce(func.sum(MatchPlayer.assists), 0),
            func.coalesce(func.avg(MatchPlayer.player_rating), 5.0),
            func.coalesce(func.sum(MatchPlayer.key_passes), 0),
        ).where(MatchPlayer.player_id == player_id)
    )
    goals, assists, avg_rating, key_passes = stats_row.one()
    goals = int(goals)
    assists = int(assists)
    avg_rating = float(avg_rating)
    key_passes = int(key_passes)

    stats_score = _clamp(
        goals * 5 + assists * 3 + (avg_rating - 5.0) * 8 + key_passes * 2
    )

    # Regularite
    total_matches = await db.scalar(
        select(func.count(MatchPlayer.match_id)).where(MatchPlayer.player_id == player_id)
    ) or 0
    regularity_score = _clamp(total_matches / 15 * 100)

    # Progression (vs score 30j avant)
    thirty_ago = datetime.utcnow() - timedelta(days=30)
    prev_score = await db.scalar(
        select(MachineScoreHistory.score)
        .where(
            MachineScoreHistory.player_id == player_id,
            MachineScoreHistory.computed_at < thirty_ago,
        )
        .order_by(MachineScoreHistory.computed_at.desc())
        .limit(1)
    ) or 0

    progression_score = _clamp(50.0 + (prev_score - 50) * 0.15)

    # Score final
    final = int(_clamp(
        social_score * 0.35
        + stats_score * 0.25
        + regularity_score * 0.25
        + progression_score * 0.15
    ))
    tier = score_to_tier(final)

    # 6 dimensions estimees
    tec = int(_clamp(stats_score * 0.8 + badge_comp))
    phy = int(_clamp(vote_comp * 0.6 + regularity_score * 0.4))
    vit = int(_clamp(50 + vote_comp * 0.3))
    def_ = int(_clamp(social_score * 0.5 + regularity_score * 0.5))
    vis = int(_clamp(key_passes * 4 + stats_score * 0.3))
    imp = int(_clamp(goals * 6 + assists * 4 + total_votm * 8))

    # Persistance
    history = MachineScoreHistory(
        player_id=player_id,
        score=final,
        tier=tier,
        tec=tec, phy=phy, vit=vit, def_=def_, vis=vis, imp=imp,
        social_component=round(social_score, 2),
        stats_component=round(stats_score, 2),
        regularity_component=round(regularity_score, 2),
        progression_component=round(progression_score, 2),
    )
    db.add(history)

    player = await db.get(Player, player_id)
    if player:
        player.machine_score = final
        player.machine_score_tier = tier
        db.add(player)

    await db.commit()
    return final
