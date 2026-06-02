from fastapi import APIRouter
from pydantic import BaseModel
from services.statsbomb import load_events
from services.tactical_engine import compute_tactical_score

router = APIRouter(prefix="/tactical", tags=["tactical"])

class TacticalRequest(BaseModel):
    match_id: int
    player_name: str
    player_position: str
    team_style: str = "positional"
    phase_config: dict = {"buildup": "4-3-3", "progression": "3-4-3", "finish": "3-2-5"}

@router.post("/score")
def get_tactical_score(req: TacticalRequest):
    events = load_events(req.match_id)
    report = compute_tactical_score(
        events_df=events,
        player_name=req.player_name,
        player_position=req.player_position,
        team_style=req.team_style,
        phase_config=req.phase_config,
        match_id=req.match_id,
    )
    return report.to_dict()
