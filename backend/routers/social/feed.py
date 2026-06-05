from __future__ import annotations
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    _: Player = Depends(get_current_player),
):
    """Get social feed posts (paginated)."""
    result = await db.execute(
        select(FeedPost, Player)
        .join(Player, Player.id == FeedPost.player_id)
        .order_by(FeedPost.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
    return [
        FeedPostOut(
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
        )
        for post, player in rows
    ]


@router.post("/{post_id}/like", status_code=204)
async def like_post(
    post_id: str,
    _: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Like a feed post (increment likes_count)."""
    post = await db.get(FeedPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likes_count += 1
    db.add(post)
    await db.commit()
