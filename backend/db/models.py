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
