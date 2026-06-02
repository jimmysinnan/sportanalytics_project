from fastapi import APIRouter
import pandas as pd
from services.statsbomb import load_events, load_lineups, get_teams_in_match
from services.viz_pitch import draw_shots, draw_pass_network
from services.viz_timeline import generate_xg_timeline, generate_events_timeline
from utils import fig_to_base64

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/{match_id}/summary")
def get_match_summary(match_id: int):
    events = load_events(match_id)
    teams = get_teams_in_match(events)
    if len(teams) < 2:
        return {"error": "teams not found"}
    home, away = teams[0], teams[1]

    def _cnt(team: str, t: str) -> int:
        if "type" not in events.columns or "team" not in events.columns:
            return 0
        return int(((events["team"] == team) & (events["type"] == t)).sum())

    home_ev = events[events["team"] == home] if "team" in events.columns else pd.DataFrame()
    away_ev = events[events["team"] == away] if "team" in events.columns else pd.DataFrame()
    total = len(home_ev) + len(away_ev)
    home_poss = round(len(home_ev) / total * 100, 1) if total > 0 else 50.0

    home_xg, away_xg = 0.0, 0.0
    if "shot_statsbomb_xg" in events.columns and "type" in events.columns:
        home_xg = round(events[(events["team"] == home) & (events["type"] == "Shot")]["shot_statsbomb_xg"].sum(), 2)
        away_xg = round(events[(events["team"] == away) & (events["type"] == "Shot")]["shot_statsbomb_xg"].sum(), 2)

    return {
        "home_team": home, "away_team": away,
        "home_possession": home_poss, "away_possession": round(100 - home_poss, 1),
        "home_shots": _cnt(home, "Shot"), "away_shots": _cnt(away, "Shot"),
        "home_passes": _cnt(home, "Pass"), "away_passes": _cnt(away, "Pass"),
        "home_xg": home_xg, "away_xg": away_xg,
    }

@router.get("/{match_id}/shots/{team_name}")
def get_shot_map(match_id: int, team_name: str):
    events = load_events(match_id)
    fig = draw_shots(events, team_name=team_name)
    return {"image_b64": fig_to_base64(fig)}

@router.get("/{match_id}/xg-timeline")
def get_xg_timeline(match_id: int):
    events = load_events(match_id)
    teams = get_teams_in_match(events)
    if len(teams) < 2:
        return {"image_b64": ""}
    fig = generate_xg_timeline(events, teams[0], teams[1])
    return {"image_b64": fig_to_base64(fig)}

@router.get("/{match_id}/pass-network/{team_name}")
def get_pass_network(match_id: int, team_name: str):
    events = load_events(match_id)
    fig = draw_pass_network(events, team_name)
    return {"image_b64": fig_to_base64(fig)}

@router.get("/{match_id}/events-timeline")
def get_events_timeline(match_id: int):
    events = load_events(match_id)
    fig = generate_events_timeline(events)
    return {"image_b64": fig_to_base64(fig)}

@router.get("/{match_id}/lineups")
def get_lineups(match_id: int):
    lineups = load_lineups(match_id)
    result = {}
    for team, df in lineups.items():
        cols = [c for c in ["player_name", "jersey_number", "country"] if c in df.columns]
        result[team] = df[cols].to_dict(orient="records") if cols else []
    return result
