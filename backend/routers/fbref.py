from fastapi import APIRouter, HTTPException
from services.fbref import (
    get_player_stats, get_team_stats, get_shooting_stats,
    get_passing_stats, SUPPORTED_LEAGUES, SUPPORTED_SEASONS
)

router = APIRouter(prefix="/fbref", tags=["fbref"])


@router.get("/leagues")
def get_leagues():
    return {"leagues": SUPPORTED_LEAGUES, "seasons": SUPPORTED_SEASONS}


@router.get("/{league}/players")
def fbref_player_stats(league: str, season: str = "2024-2025"):
    df = get_player_stats(league, season)
    if df.empty:
        raise HTTPException(503, "FBref data unavailable — check network or season")
    cols = [c for c in ["player", "team", "pos", "age", "games", "goals", "assists",
                         "xg", "xg_assist", "progressive_passes", "progressive_carries"]
            if c in df.columns]
    return {"players": df[cols if cols else df.columns.tolist()[:15]].to_dict(orient="records"),
            "total": len(df)}


@router.get("/{league}/teams")
def fbref_team_stats(league: str, season: str = "2024-2025"):
    df = get_team_stats(league, season)
    if df.empty:
        raise HTTPException(503, "FBref data unavailable")
    return {"teams": df.to_dict(orient="records"), "total": len(df)}


@router.get("/{league}/shooting")
def fbref_shooting_stats(league: str, season: str = "2024-2025"):
    df = get_shooting_stats(league, season)
    if df.empty:
        raise HTTPException(503, "FBref shooting data unavailable")
    cols = [c for c in ["player", "team", "shots", "shots_on_target", "goals", "xg", "xg_per_shot"]
            if c in df.columns]
    return {"players": df[cols if cols else df.columns.tolist()[:12]].to_dict(orient="records")}


@router.get("/{league}/passing")
def fbref_passing_stats(league: str, season: str = "2024-2025"):
    df = get_passing_stats(league, season)
    if df.empty:
        raise HTTPException(503, "FBref passing data unavailable")
    cols = [c for c in ["player", "team", "passes_completed", "passes", "pass_pct",
                         "progressive_passes", "key_passes"]
            if c in df.columns]
    return {"players": df[cols if cols else df.columns.tolist()[:12]].to_dict(orient="records")}
