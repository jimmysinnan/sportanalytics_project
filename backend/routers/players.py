from fastapi import APIRouter, HTTPException
import numpy as np
from services.statsbomb import (
    load_events, get_players_in_match, aggregate_player_stats
)
from services.metrics import (
    build_full_player_metrics, tactical_summary_text,
    calculate_pressing_intensity, calculate_progressive_passes,
    calculate_defensive_actions,
)
from services.viz_heatmap import generate_heatmap
from services.viz_radar import generate_radar
from utils import fig_to_base64

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/{match_id}/list")
def get_players(match_id: int):
    events = load_events(match_id)
    return {"players": get_players_in_match(events)}

@router.get("/{match_id}/{player_name}/stats")
def get_player_stats(match_id: int, player_name: str):
    events = load_events(match_id)
    metrics = build_full_player_metrics(events, player_name)
    position = "Center Midfield"
    if "position" in events.columns:
        pos = events[events["player"] == player_name]["position"].dropna()
        if not pos.empty:
            position = str(pos.iloc[0])
    summary = tactical_summary_text(metrics, player_name, position)
    return {"metrics": metrics, "position": position, "summary": summary}

@router.get("/{match_id}/{player_name}/heatmap")
def get_heatmap(match_id: int, player_name: str,
                action_type: str = "all", period: str = "full"):
    events = load_events(match_id)
    fig = generate_heatmap(events, player_name=player_name,
                           action_type=action_type, period=period)
    return {"image_b64": fig_to_base64(fig)}

@router.get("/{match_id}/{player_name}/radar")
def get_radar(match_id: int, player_name: str):
    events = load_events(match_id)
    metrics = build_full_player_metrics(events, player_name)
    position = "Center Midfield"
    if "position" in events.columns:
        pos = events[events["player"] == player_name]["position"].dropna()
        if not pos.empty:
            position = str(pos.iloc[0])

    sample = get_players_in_match(events)[:12]
    all_stats = [aggregate_player_stats(events, p) for p in sample]
    valid = [s for s in all_stats if s]
    bench = {}
    if valid:
        for k in valid[0].keys():
            bench[k] = round(np.mean([float(s.get(k, 0) or 0) for s in valid]), 2)
        bench["progressive_passes"] = round(
            np.mean([calculate_progressive_passes(events, p) for p in sample[:8]]), 2)
        bench["pressing_intensity"] = round(
            np.mean([calculate_pressing_intensity(events, p) for p in sample[:8]]), 3)
        bench["defensive_actions"] = round(
            np.mean([calculate_defensive_actions(events, p) for p in sample[:8]]), 2)

    fig = generate_radar(player_stats=metrics, player_name=player_name,
                         position=position, benchmark_stats=bench or None)
    return {"image_b64": fig_to_base64(fig)}
