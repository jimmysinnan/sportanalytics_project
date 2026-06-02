from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
import numpy as np
from services.statsbomb import load_events, get_players_in_match, aggregate_player_stats
from services.metrics import (
    build_full_player_metrics, tactical_summary_text,
    calculate_pressing_intensity, calculate_progressive_passes, calculate_defensive_actions,
)
from services.viz_heatmap import generate_heatmap
from services.viz_radar import generate_radar
from services.pdf_generator import PlayerReport

router = APIRouter(prefix="/pdf", tags=["pdf"])

class PdfRequest(BaseModel):
    match_id: int
    player_name: str
    position: str
    competition_label: str
    observations: str = ""

@router.post("/player")
def generate_player_pdf(req: PdfRequest):
    events = load_events(req.match_id)
    metrics = build_full_player_metrics(events, req.player_name)

    position = req.position
    if "position" in events.columns:
        pos = events[events["player"] == req.player_name]["position"].dropna()
        if not pos.empty:
            position = str(pos.iloc[0])

    sample = get_players_in_match(events)[:8]
    all_stats = [aggregate_player_stats(events, p) for p in sample]
    valid = [s for s in all_stats if s]
    bench = {}
    if valid:
        for k in valid[0].keys():
            bench[k] = round(np.mean([float(s.get(k, 0) or 0) for s in valid]), 2)
        bench["progressive_passes"] = round(np.mean([calculate_progressive_passes(events, p) for p in sample]), 2)
        bench["pressing_intensity"] = round(np.mean([calculate_pressing_intensity(events, p) for p in sample]), 3)
        bench["defensive_actions"] = round(np.mean([calculate_defensive_actions(events, p) for p in sample]), 2)

    hm_fig = generate_heatmap(events, player_name=req.player_name, action_type="all", period="full")
    radar_fig = generate_radar(player_stats=metrics, player_name=req.player_name,
                               position=position, benchmark_stats=bench or None)

    observations = req.observations or tactical_summary_text(metrics, req.player_name, position)
    observations = observations.replace("**", "").replace("*", "")

    report = PlayerReport()
    report.add_header(req.player_name, {
        "match": f"Match #{req.match_id}",
        "date": "",
        "compétition": req.competition_label,
        "poste": req.position,
    })
    report.add_stats_table(metrics)
    report.add_figure(hm_fig, "Heatmap — Zones d'activité")
    report.add_figure(radar_fig, "Radar Tactique")
    report.add_observations(observations)
    pdf_bytes = report.generate()

    filename = f"rapport_{req.player_name.replace(' ', '_')}_{req.match_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
