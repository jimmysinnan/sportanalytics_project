"""
StatsBomb Open Data loader — no API key required.
Uses statsbombpy which ships with free open-data access.
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd
from statsbombpy import sb


# ── Competitions / seasons ────────────────────────────────────────────────────

@lru_cache(maxsize=64)
def list_competitions() -> pd.DataFrame:
    """Return all available StatsBomb open-data competitions."""
    try:
        comps = sb.competitions()
        return comps
    except Exception:
        return pd.DataFrame()


@lru_cache(maxsize=64)
def list_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    """Return all matches for a given competition / season."""
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        return matches
    except Exception:
        return pd.DataFrame()


# ── Events ────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=64)
def load_events(match_id: int) -> pd.DataFrame:
    """Return all events for a match (flat JSON → DataFrame)."""
    try:
        events = sb.events(match_id=match_id, split=False, flatten_attrs=True)
        return events
    except Exception:
        return pd.DataFrame()


@lru_cache(maxsize=64)
def load_lineups(match_id: int) -> dict[str, pd.DataFrame]:
    """Return lineups dict {team_name: DataFrame} for a match."""
    try:
        lineups = sb.lineups(match_id=match_id)
        return lineups
    except Exception:
        return {}


# ── Player helpers ────────────────────────────────────────────────────────────

def get_player_events(events: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Filter events DataFrame for one player."""
    if events.empty or "player" not in events.columns:
        return pd.DataFrame()
    return events[events["player"] == player_name].copy()


def get_players_in_match(events: pd.DataFrame) -> list[str]:
    """Return sorted list of player names who appear in events."""
    if events.empty or "player" not in events.columns:
        return []
    return sorted(events["player"].dropna().unique().tolist())


def get_match_label(row: pd.Series) -> str:
    """Build a human-readable match label from a matches row."""
    home = row.get("home_team", "?")
    away = row.get("away_team", "?")
    date = row.get("match_date", "")
    score_h = row.get("home_score", "")
    score_a = row.get("away_score", "")
    return f"{home} {score_h}–{score_a} {away}  ({date})"


# ── Match / team helpers ──────────────────────────────────────────────────────

def get_teams_in_match(events: pd.DataFrame) -> list[str]:
    """Return the two team names in a match."""
    if events.empty or "team" not in events.columns:
        return []
    return sorted(events["team"].dropna().unique().tolist())


def get_team_events(events: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """Filter events for a team."""
    if events.empty or "team" not in events.columns:
        return pd.DataFrame()
    return events[events["team"] == team_name].copy()


# ── Player stats aggregation ──────────────────────────────────────────────────

def aggregate_player_stats(events: pd.DataFrame, player_name: str) -> dict:
    """
    Compute a summary dict of basic stats for a player from events.
    """
    pe = get_player_events(events, player_name)
    if pe.empty:
        return {}

    stats: dict = {}

    # Minutes on field (approx from last event minute)
    stats["minutes"] = int(pe["minute"].max()) if "minute" in pe.columns else 0

    # Goals
    shots = pe[pe["type"] == "Shot"] if "type" in pe.columns else pd.DataFrame()
    if not shots.empty and "shot_outcome" in shots.columns:
        stats["goals"] = int((shots["shot_outcome"] == "Goal").sum())
        stats["shots"] = len(shots)
        stats["shots_on_target"] = int(
            shots["shot_outcome"].isin(["Goal", "Saved"]).sum()
            if "shot_outcome" in shots.columns else 0
        )
        stats["xg"] = round(shots["shot_statsbomb_xg"].sum(), 2) if "shot_statsbomb_xg" in shots.columns else 0.0
    else:
        stats["goals"] = 0
        stats["shots"] = 0
        stats["shots_on_target"] = 0
        stats["xg"] = 0.0

    # Passes
    passes = pe[pe["type"] == "Pass"] if "type" in pe.columns else pd.DataFrame()
    if not passes.empty:
        stats["passes"] = len(passes)
        if "pass_outcome" in passes.columns:
            completed = passes["pass_outcome"].isna().sum()  # NaN = completed in SB
            stats["pass_completion"] = round(completed / len(passes) * 100, 1)
        else:
            stats["pass_completion"] = 0.0
        if "pass_key_pass" in passes.columns:
            stats["key_passes"] = int(passes["pass_key_pass"].sum())
        else:
            stats["key_passes"] = 0
        if "pass_goal_assist" in passes.columns:
            stats["assists"] = int(passes["pass_goal_assist"].fillna(False).sum())
        else:
            stats["assists"] = 0
    else:
        stats["passes"] = 0
        stats["pass_completion"] = 0.0
        stats["key_passes"] = 0
        stats["assists"] = 0

    # Dribbles
    if "type" in pe.columns:
        dribbles = pe[pe["type"] == "Dribble"]
        stats["dribbles_attempted"] = len(dribbles)
        if not dribbles.empty and "dribble_outcome" in dribbles.columns:
            stats["dribbles_completed"] = int((dribbles["dribble_outcome"] == "Complete").sum())
        else:
            stats["dribbles_completed"] = 0
    else:
        stats["dribbles_attempted"] = 0
        stats["dribbles_completed"] = 0

    # Pressures
    if "type" in pe.columns:
        stats["pressures"] = int((pe["type"] == "Pressure").sum())
    else:
        stats["pressures"] = 0

    # Duels
    if "type" in pe.columns:
        duels = pe[pe["type"] == "Duel"]
        stats["duels"] = len(duels)
        if not duels.empty and "duel_outcome" in duels.columns:
            won = duels["duel_outcome"].isin(["Won", "Success In Play", "Success Out"])
            stats["duels_won"] = int(won.sum())
        else:
            stats["duels_won"] = 0
    else:
        stats["duels"] = 0
        stats["duels_won"] = 0

    # Ball receipts / carries
    if "type" in pe.columns:
        stats["carries"] = int((pe["type"] == "Carry").sum())
        stats["ball_receipts"] = int((pe["type"] == "Ball Receipt*").sum())
    else:
        stats["carries"] = 0
        stats["ball_receipts"] = 0

    return stats
