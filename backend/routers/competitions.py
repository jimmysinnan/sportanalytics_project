from fastapi import APIRouter, HTTPException
from services.statsbomb import list_competitions, list_matches, get_match_label

router = APIRouter(prefix="/competitions", tags=["competitions"])

@router.get("/")
def get_competitions():
    df = list_competitions()
    if df.empty:
        raise HTTPException(503, "StatsBomb data unavailable")
    cols = [c for c in ["competition_id", "season_id", "competition_name",
                         "season_name", "country_name", "competition_gender"]
            if c in df.columns]
    records = df[cols].drop_duplicates().to_dict(orient="records")
    return {"competitions": records}

@router.get("/{competition_id}/seasons/{season_id}/matches")
def get_matches(competition_id: int, season_id: int):
    df = list_matches(competition_id, season_id)
    if df.empty:
        return {"matches": []}
    records = []
    for _, row in df.iterrows():
        records.append({
            "match_id": int(row["match_id"]),
            "label": get_match_label(row),
            "home_team": str(row.get("home_team", "")),
            "away_team": str(row.get("away_team", "")),
            "home_score": row.get("home_score", ""),
            "away_score": row.get("away_score", ""),
            "match_date": str(row.get("match_date", "")),
        })
    return {"matches": records}
