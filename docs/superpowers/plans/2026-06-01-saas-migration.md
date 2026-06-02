# la soccer Machine — Migration SaaS : FastAPI + Next.js

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrer l'app Streamlit vers une vraie architecture SaaS découplée — FastAPI (Python) pour les analytics, Next.js (React) pour l'interface — déployable en 10 minutes sur Railway + Vercel.

**Architecture:** Le backend FastAPI expose des endpoints REST qui encapsulent toute la logique Python existante (statsbombpy, mplsoccer, pandas). Les figures matplotlib sont sérialisées en base64 PNG. Le frontend Next.js 14 (App Router) consomme ces endpoints et affiche les visualisations dans une UI dark-mode branded "la soccer Machine".

**Tech Stack:** FastAPI 0.115 · Python 3.11 · statsbombpy · mplsoccer · pandas · fpdf2 | Next.js 14 App Router · TypeScript · Tailwind CSS · shadcn/ui · Recharts (xG timeline)

**Pourquoi pas Streamlit ?**
- Streamlit lie le cycle de rendu Python au frontend → pas extensible, conflits de versions Python
- Pas de routing réel, pas d'auth, pas d'API publique pour des intégrations tierces
- FastAPI + Next.js = stack standard SaaS, déployable séparément, maintenable long terme

---

## Prérequis

- Python 3.11+ (`python --version`)
- Node.js 20+ (`node --version`)
- Git configuré
- Compte Railway (backend) + Vercel (frontend) — gratuits pour commencer

---

## Structure des fichiers cible

```
sportanalytics/
├── backend/
│   ├── main.py                    ← FastAPI app entry point
│   ├── routers/
│   │   ├── competitions.py        ← GET /competitions, /matches
│   │   ├── players.py             ← GET /player/stats, /player/radar, /player/heatmap
│   │   ├── match.py               ← GET /match/shots, /match/xg, /match/network
│   │   ├── tactical.py            ← POST /tactical/score
│   │   └── pdf.py                 ← POST /pdf/player
│   ├── services/
│   │   ├── statsbomb.py           ← wrappers statsbombpy (inchangés)
│   │   ├── metrics.py             ← copie utils/metrics.py
│   │   ├── tactical_engine.py     ← copie engine/tactical_engine.py
│   │   ├── viz_heatmap.py         ← copie viz/heatmap.py
│   │   ├── viz_radar.py           ← copie viz/radar.py
│   │   ├── viz_pitch.py           ← copie viz/pitch.py
│   │   ├── viz_timeline.py        ← copie viz/timeline.py
│   │   └── pdf_generator.py       ← copie reports/pdf_generator.py
│   ├── utils.py                   ← fig_to_base64(), shared helpers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         ← root layout, sidebar, dark theme
│   │   │   ├── page.tsx           ← page d'accueil
│   │   │   ├── profil/page.tsx
│   │   │   ├── heatmap/page.tsx
│   │   │   ├── match/page.tsx
│   │   │   ├── rapport/page.tsx
│   │   │   └── tactique/page.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── Sidebar.tsx
│   │   │   ├── selectors/
│   │   │   │   ├── CompetitionSelect.tsx
│   │   │   │   ├── MatchSelect.tsx
│   │   │   │   └── PlayerSelect.tsx
│   │   │   └── analytics/
│   │   │       ├── KpiGrid.tsx
│   │   │       ├── PitchImage.tsx
│   │   │       ├── XgTimeline.tsx
│   │   │       └── TacticalScore.tsx
│   │   └── lib/
│   │       ├── api.ts             ← fetch wrapper typé
│   │       └── types.ts           ← interfaces TypeScript
│   ├── tailwind.config.ts
│   └── package.json
├── docker-compose.yml             ← dev local full-stack
└── .env.example
```

---

## Task 1 : Bootstrap backend FastAPI

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/utils.py`

- [ ] **Step 1 : Créer `backend/requirements.txt`**

```
fastapi>=0.115
uvicorn[standard]>=0.30
statsbombpy>=1.18
mplsoccer>=1.6
pandas>=2.0
numpy>=1.26
matplotlib>=3.8
scipy>=1.11
fpdf2>=2.7
Pillow>=10.0
python-multipart>=0.0.10
```

- [ ] **Step 2 : Créer l'environnement virtuel et installer**

```bash
cd backend
python -m venv .venv
# Windows :
.venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] **Step 3 : Créer `backend/utils.py`**

```python
import io, base64
import matplotlib.pyplot as plt

def fig_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
```

- [ ] **Step 4 : Créer `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="la soccer Machine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5 : Vérifier que le serveur démarre**

```bash
uvicorn main:app --reload --port 8000
# Ouvrir : http://localhost:8000/health
# Réponse attendue : {"status": "ok"}
```

- [ ] **Step 6 : Commit**

```bash
git add backend/
git commit -m "feat(backend): bootstrap FastAPI avec CORS et health check"
```

---

## Task 2 : Copier et adapter les services Python

**Files:**
- Create: `backend/services/statsbomb.py`
- Create: `backend/services/metrics.py`
- Create: `backend/services/tactical_engine.py`
- Create: `backend/services/viz_heatmap.py`
- Create: `backend/services/viz_radar.py`
- Create: `backend/services/viz_pitch.py`
- Create: `backend/services/viz_timeline.py`
- Create: `backend/services/pdf_generator.py`

- [ ] **Step 1 : Copier les services depuis le projet Streamlit**

```bash
# Depuis la racine du projet
cp data/loaders/statsbomb_loader.py backend/services/statsbomb.py
cp utils/metrics.py                  backend/services/metrics.py
cp engine/tactical_engine.py         backend/services/tactical_engine.py
cp viz/heatmap.py                    backend/services/viz_heatmap.py
cp viz/radar.py                      backend/services/viz_radar.py
cp viz/pitch.py                      backend/services/viz_pitch.py
cp viz/timeline.py                   backend/services/viz_timeline.py
cp reports/pdf_generator.py          backend/services/pdf_generator.py
```

- [ ] **Step 2 : Supprimer les imports `streamlit` dans `backend/services/statsbomb.py`**

Remplacer les lignes avec `import streamlit as st` et les `@st.cache_data` par un cache simple :

```python
# backend/services/statsbomb.py
from __future__ import annotations
from functools import lru_cache
import pandas as pd
from statsbombpy import sb

@lru_cache(maxsize=1)
def list_competitions() -> pd.DataFrame:
    try:
        return sb.competitions()
    except Exception:
        return pd.DataFrame()

@lru_cache(maxsize=64)
def list_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    try:
        return sb.matches(competition_id=competition_id, season_id=season_id)
    except Exception:
        return pd.DataFrame()

@lru_cache(maxsize=32)
def load_events(match_id: int) -> pd.DataFrame:
    try:
        return sb.events(match_id=match_id, split=False, flatten_attrs=True)
    except Exception:
        return pd.DataFrame()

@lru_cache(maxsize=32)
def load_lineups(match_id: int) -> dict:
    try:
        return sb.lineups(match_id=match_id)
    except Exception:
        return {}

def get_player_events(events: pd.DataFrame, player_name: str) -> pd.DataFrame:
    if events.empty or "player" not in events.columns:
        return pd.DataFrame()
    return events[events["player"] == player_name].copy()

def get_players_in_match(events: pd.DataFrame) -> list[str]:
    if events.empty or "player" not in events.columns:
        return []
    return sorted(events["player"].dropna().unique().tolist())

def get_teams_in_match(events: pd.DataFrame) -> list[str]:
    if events.empty or "team" not in events.columns:
        return []
    return sorted(events["team"].dropna().unique().tolist())

def get_match_label(row: pd.Series) -> str:
    home = row.get("home_team", "?")
    away = row.get("away_team", "?")
    date = row.get("match_date", "")
    score_h = row.get("home_score", "")
    score_a = row.get("away_score", "")
    return f"{home} {score_h}–{score_a} {away}  ({date})"

def aggregate_player_stats(events: pd.DataFrame, player_name: str) -> dict:
    from backend.services.statsbomb import get_player_events
    pe = get_player_events(events, player_name)
    if pe.empty:
        return {}
    stats: dict = {}
    stats["minutes"] = int(pe["minute"].max()) if "minute" in pe.columns else 0
    shots = pe[pe["type"] == "Shot"] if "type" in pe.columns else pd.DataFrame()
    if not shots.empty and "shot_outcome" in shots.columns:
        stats["goals"] = int((shots["shot_outcome"] == "Goal").sum())
        stats["shots"] = len(shots)
        stats["shots_on_target"] = int(shots["shot_outcome"].isin(["Goal", "Saved"]).sum())
        stats["xg"] = round(shots["shot_statsbomb_xg"].sum(), 2) if "shot_statsbomb_xg" in shots.columns else 0.0
    else:
        stats.update({"goals": 0, "shots": 0, "shots_on_target": 0, "xg": 0.0})
    passes = pe[pe["type"] == "Pass"] if "type" in pe.columns else pd.DataFrame()
    if not passes.empty:
        stats["passes"] = len(passes)
        completed = passes["pass_outcome"].isna().sum() if "pass_outcome" in passes.columns else 0
        stats["pass_completion"] = round(completed / len(passes) * 100, 1)
        stats["key_passes"] = int(passes["pass_key_pass"].sum()) if "pass_key_pass" in passes.columns else 0
        stats["assists"] = int(passes["pass_goal_assist"].fillna(False).sum()) if "pass_goal_assist" in passes.columns else 0
    else:
        stats.update({"passes": 0, "pass_completion": 0.0, "key_passes": 0, "assists": 0})
    if "type" in pe.columns:
        dribbles = pe[pe["type"] == "Dribble"]
        stats["dribbles_attempted"] = len(dribbles)
        stats["dribbles_completed"] = int((dribbles["dribble_outcome"] == "Complete").sum()) if (not dribbles.empty and "dribble_outcome" in dribbles.columns) else 0
        stats["pressures"] = int((pe["type"] == "Pressure").sum())
        duels = pe[pe["type"] == "Duel"]
        stats["duels"] = len(duels)
        stats["duels_won"] = int(duels["duel_outcome"].isin(["Won", "Success In Play", "Success Out"]).sum()) if (not duels.empty and "duel_outcome" in duels.columns) else 0
        stats["carries"] = int((pe["type"] == "Carry").sum())
        stats["ball_receipts"] = int((pe["type"] == "Ball Receipt*").sum())
    else:
        stats.update({"dribbles_attempted": 0, "dribbles_completed": 0, "pressures": 0,
                      "duels": 0, "duels_won": 0, "carries": 0, "ball_receipts": 0})
    return stats
```

- [ ] **Step 3 : Adapter les imports dans `backend/services/metrics.py`**

Remplacer `from data.loaders.statsbomb_loader import` par `from backend.services.statsbomb import`

- [ ] **Step 4 : Créer `backend/services/__init__.py` vide**

```bash
touch backend/services/__init__.py
```

- [ ] **Step 5 : Vérifier que les imports fonctionnent**

```bash
cd backend
python -c "from services.statsbomb import list_competitions; print(list_competitions().shape)"
# Attendu : (N, M) — affiche les dimensions du DataFrame
```

- [ ] **Step 6 : Commit**

```bash
git add backend/services/
git commit -m "feat(backend): migration services Python depuis Streamlit"
```

---

## Task 3 : Router `/competitions` et `/matches`

**Files:**
- Create: `backend/routers/competitions.py`

- [ ] **Step 1 : Créer `backend/routers/competitions.py`**

```python
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
            "home_team": row.get("home_team", ""),
            "away_team": row.get("away_team", ""),
            "home_score": row.get("home_score", ""),
            "away_score": row.get("away_score", ""),
            "match_date": str(row.get("match_date", "")),
        })
    return {"matches": records}
```

- [ ] **Step 2 : Enregistrer le router dans `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.competitions import router as competitions_router

app = FastAPI(title="la soccer Machine API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.include_router(competitions_router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 3 : Tester les endpoints**

```bash
uvicorn main:app --reload --port 8000
curl http://localhost:8000/competitions/ | python -m json.tool | head -30
curl "http://localhost:8000/competitions/11/seasons/90/matches" | python -m json.tool
# competitions_id=11 = La Liga, season_id=90 = 2020/21
```

- [ ] **Step 4 : Commit**

```bash
git add backend/routers/ backend/main.py
git commit -m "feat(backend): endpoints competitions et matches"
```

---

## Task 4 : Router `/players` — stats, heatmap, radar

**Files:**
- Create: `backend/routers/players.py`

- [ ] **Step 1 : Créer `backend/routers/players.py`**

```python
from fastapi import APIRouter, HTTPException
from services.statsbomb import (
    load_events, get_players_in_match, aggregate_player_stats
)
from services.metrics import build_full_player_metrics, tactical_summary_text
from services.viz_heatmap import generate_heatmap
from services.viz_radar import generate_radar
from utils import fig_to_base64
import numpy as np

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

    # Quick benchmark: average of first 12 players
    from services.metrics import (
        calculate_pressing_intensity, calculate_progressive_passes,
        calculate_defensive_actions
    )
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
```

- [ ] **Step 2 : Ajouter le router dans `backend/main.py`**

```python
from routers.players import router as players_router
app.include_router(players_router)
```

- [ ] **Step 3 : Tester**

```bash
curl "http://localhost:8000/players/3764468/Lionel%20Messi/stats" | python -m json.tool
# Remplacer 3764468 par un match_id valide depuis /competitions/
```

- [ ] **Step 4 : Commit**

```bash
git add backend/routers/players.py backend/main.py
git commit -m "feat(backend): endpoints stats, heatmap, radar joueur"
```

---

## Task 5 : Router `/match` — shot map, xG, réseau de passes

**Files:**
- Create: `backend/routers/match.py`

- [ ] **Step 1 : Créer `backend/routers/match.py`**

```python
from fastapi import APIRouter
from services.statsbomb import load_events, load_lineups, get_teams_in_match
from services.viz_pitch import draw_shots, draw_pass_network
from services.viz_timeline import generate_xg_timeline, generate_events_timeline
from utils import fig_to_base64
import pandas as pd

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

@router.get("/{match_id}/lineups")
def get_lineups(match_id: int):
    lineups = load_lineups(match_id)
    result = {}
    for team, df in lineups.items():
        cols = [c for c in ["player_name", "jersey_number", "country"] if c in df.columns]
        result[team] = df[cols].to_dict(orient="records") if cols else []
    return result
```

- [ ] **Step 2 : Ajouter dans `main.py`**

```python
from routers.match import router as match_router
app.include_router(match_router)
```

- [ ] **Step 3 : Commit**

```bash
git add backend/routers/match.py backend/main.py
git commit -m "feat(backend): endpoints analyse match (shots, xG, passes)"
```

---

## Task 6 : Router `/tactical` et `/pdf`

**Files:**
- Create: `backend/routers/tactical.py`
- Create: `backend/routers/pdf.py`

- [ ] **Step 1 : Créer `backend/routers/tactical.py`**

```python
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
```

- [ ] **Step 2 : Créer `backend/routers/pdf.py`**

```python
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from services.statsbomb import load_events, get_players_in_match, aggregate_player_stats
from services.metrics import build_full_player_metrics, tactical_summary_text
from services.viz_heatmap import generate_heatmap
from services.viz_radar import generate_radar
from services.pdf_generator import PlayerReport
from services.metrics import (
    calculate_pressing_intensity, calculate_progressive_passes, calculate_defensive_actions
)
import numpy as np

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
```

- [ ] **Step 3 : Ajouter dans `main.py`**

```python
from routers.tactical import router as tactical_router
from routers.pdf import router as pdf_router
app.include_router(tactical_router)
app.include_router(pdf_router)
```

- [ ] **Step 4 : Tester l'API complète**

```bash
curl http://localhost:8000/docs
# Ouvrir dans le navigateur — Swagger UI doit afficher tous les endpoints
```

- [ ] **Step 5 : Commit**

```bash
git add backend/routers/tactical.py backend/routers/pdf.py backend/main.py
git commit -m "feat(backend): endpoints tactical score et génération PDF"
```

---

## Task 7 : Bootstrap frontend Next.js

**Files:**
- Create: `frontend/` (projet Next.js)
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/types.ts`

- [ ] **Step 1 : Créer le projet Next.js**

```bash
cd sportanalytics
npx create-next-app@latest frontend \
  --typescript --tailwind --eslint --app --src-dir \
  --no-import-alias
cd frontend
```

- [ ] **Step 2 : Installer les dépendances UI**

```bash
npm install @radix-ui/react-select @radix-ui/react-tabs recharts lucide-react clsx
npx shadcn@latest init
# Choisir : Dark mode → yes, Slate base color
npx shadcn@latest add select tabs card badge button
```

- [ ] **Step 3 : Configurer le thème dark "la soccer Machine" dans `tailwind.config.ts`**

```typescript
import type { Config } from "tailwindcss";
const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          bg:      "#0f1f14",
          sidebar: "#1a4d2e",
          gold:    "#d4a017",
          muted:   "#a8c5b0",
          text:    "#e8e8e8",
        },
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 4 : Créer `frontend/src/lib/types.ts`**

```typescript
export interface Competition {
  competition_id: number;
  season_id: number;
  competition_name: string;
  season_name: string;
  country_name: string;
}

export interface Match {
  match_id: number;
  label: string;
  home_team: string;
  away_team: string;
  home_score: string | number;
  away_score: string | number;
  match_date: string;
}

export interface PlayerMetrics {
  minutes: number;
  goals: number;
  assists: number;
  passes: number;
  pass_completion: number;
  pressures: number;
  duels: number;
  duels_won: number;
  xg: number;
  progressive_passes: number;
  pressing_intensity: number;
  defensive_actions: number;
  [key: string]: number;
}

export interface MatchSummary {
  home_team: string;
  away_team: string;
  home_possession: number;
  away_possession: number;
  home_shots: number;
  away_shots: number;
  home_passes: number;
  away_passes: number;
  home_xg: number;
  away_xg: number;
}

export interface TacticalReport {
  player_name: string;
  match_id: number;
  tactical_compatibility_score: number;
  pressing_triggers: number;
  vertical_passes_ratio: number;
  counterpressing_efficiency: number;
  versatility_score: number;
  false_nine_drops: number;
  half_space_runs: number;
  distance_estimate_km: number;
  possession_share: number;
  tactical_feedback: string[];
}
```

- [ ] **Step 5 : Créer `frontend/src/lib/api.ts`**

```typescript
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

import type { Competition, Match, PlayerMetrics, MatchSummary, TacticalReport } from "./types";

export const api = {
  competitions: (): Promise<{ competitions: Competition[] }> =>
    get("/competitions/"),

  matches: (compId: number, seasonId: number): Promise<{ matches: Match[] }> =>
    get(`/competitions/${compId}/seasons/${seasonId}/matches`),

  players: (matchId: number): Promise<{ players: string[] }> =>
    get(`/players/${matchId}/list`),

  playerStats: (matchId: number, player: string): Promise<{ metrics: PlayerMetrics; position: string; summary: string }> =>
    get(`/players/${matchId}/${encodeURIComponent(player)}/stats`),

  heatmap: (matchId: number, player: string, action = "all", period = "full"): Promise<{ image_b64: string }> =>
    get(`/players/${matchId}/${encodeURIComponent(player)}/heatmap?action_type=${action}&period=${period}`),

  radar: (matchId: number, player: string): Promise<{ image_b64: string }> =>
    get(`/players/${matchId}/${encodeURIComponent(player)}/radar`),

  matchSummary: (matchId: number): Promise<MatchSummary> =>
    get(`/match/${matchId}/summary`),

  shotMap: (matchId: number, team: string): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/shots/${encodeURIComponent(team)}`),

  xgTimeline: (matchId: number): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/xg-timeline`),

  passNetwork: (matchId: number, team: string): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/pass-network/${encodeURIComponent(team)}`),

  tacticalScore: (body: {
    match_id: number; player_name: string; player_position: string;
    team_style: string; phase_config: Record<string, string>;
  }): Promise<TacticalReport> =>
    post("/tactical/score", body),

  downloadPdf: async (body: {
    match_id: number; player_name: string; position: string;
    competition_label: string; observations: string;
  }): Promise<Blob> => {
    const res = await fetch(`${BASE}/pdf/player`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return res.blob();
  },
};
```

- [ ] **Step 6 : Vérifier que le projet compile**

```bash
npm run build
# Expected: ✓ Compiled successfully
```

- [ ] **Step 7 : Commit**

```bash
git add frontend/
git commit -m "feat(frontend): bootstrap Next.js avec types et client API"
```

---

## Task 8 : Layout global et Sidebar

**Files:**
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`

- [ ] **Step 1 : Créer `frontend/src/components/layout/Sidebar.tsx`**

```tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, User, Flame, BarChart2, FileText, Compass } from "lucide-react";

const NAV = [
  { href: "/",         label: "Accueil",       icon: Home },
  { href: "/profil",   label: "Profil Joueur", icon: User },
  { href: "/heatmap",  label: "Heatmap",        icon: Flame },
  { href: "/match",    label: "Analyse Match",  icon: BarChart2 },
  { href: "/rapport",  label: "Rapport PDF",    icon: FileText },
  { href: "/tactique", label: "Analyse Tactique", icon: Compass },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-56 shrink-0 bg-brand-sidebar border-r border-brand-gold/40 flex flex-col min-h-screen">
      <div className="p-6 text-center border-b border-brand-gold/30">
        <span className="text-2xl">⚽</span>
        <p className="text-brand-gold font-extrabold text-lg tracking-wide mt-1">
          la soccer Machine
        </p>
        <p className="text-brand-muted text-xs tracking-widest uppercase">
          Sport Analytics
        </p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                ${active
                  ? "bg-brand-gold/20 text-brand-gold font-semibold"
                  : "text-brand-text hover:text-brand-gold hover:bg-brand-gold/10"}`}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 text-xs text-brand-muted/60 border-t border-brand-gold/20">
        <p>Data: StatsBomb Open Data</p>
        <p>© 2026 la soccer Machine</p>
      </div>
    </aside>
  );
}
```

- [ ] **Step 2 : Créer `frontend/src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Sidebar from "@/components/layout/Sidebar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "la soccer Machine | Analytics",
  description: "Plateforme d'analyse tactique professionnelle",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className="dark">
      <body className={`${inter.className} bg-brand-bg text-brand-text flex min-h-screen`}>
        <Sidebar />
        <main className="flex-1 overflow-auto">{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 3 : Ajouter les styles de base dans `globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #0f1f14;
  --foreground: #e8e8e8;
}
body { background-color: var(--background); color: var(--foreground); }
```

- [ ] **Step 4 : Commit**

```bash
git add frontend/src/app/layout.tsx frontend/src/components/
git commit -m "feat(frontend): layout global et sidebar navigable"
```

---

## Task 9 : Composants réutilisables

**Files:**
- Create: `frontend/src/components/selectors/CompetitionSelect.tsx`
- Create: `frontend/src/components/selectors/MatchSelect.tsx`
- Create: `frontend/src/components/selectors/PlayerSelect.tsx`
- Create: `frontend/src/components/analytics/KpiGrid.tsx`
- Create: `frontend/src/components/analytics/PitchImage.tsx`

- [ ] **Step 1 : Créer `frontend/src/components/selectors/CompetitionSelect.tsx`**

```tsx
"use client";
import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";
import type { Competition } from "@/lib/types";

interface Props {
  onSelect: (comp: Competition) => void;
}

export default function CompetitionSelect({ onSelect }: Props) {
  const [comps, setComps] = useState<Competition[]>([]);

  useEffect(() => {
    api.competitions().then(d => setComps(d.competitions));
  }, []);

  function handleChange(val: string) {
    const [cId, sId] = val.split("|").map(Number);
    const comp = comps.find(c => c.competition_id === cId && c.season_id === sId);
    if (comp) onSelect(comp);
  }

  return (
    <Select onValueChange={handleChange}>
      <SelectTrigger className="w-full bg-brand-sidebar border-brand-gold/40 text-brand-text">
        <SelectValue placeholder="Compétition / Saison" />
      </SelectTrigger>
      <SelectContent className="bg-brand-sidebar border-brand-gold/40">
        {comps.map(c => (
          <SelectItem
            key={`${c.competition_id}|${c.season_id}`}
            value={`${c.competition_id}|${c.season_id}`}
            className="text-brand-text focus:bg-brand-gold/20 focus:text-brand-gold"
          >
            {c.competition_name} — {c.season_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

- [ ] **Step 2 : Créer `frontend/src/components/selectors/MatchSelect.tsx`**

```tsx
"use client";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Match } from "@/lib/types";

interface Props { matches: Match[]; onSelect: (m: Match) => void; }

export default function MatchSelect({ matches, onSelect }: Props) {
  return (
    <Select onValueChange={val => {
      const m = matches.find(x => String(x.match_id) === val);
      if (m) onSelect(m);
    }}>
      <SelectTrigger className="w-full bg-brand-sidebar border-brand-gold/40 text-brand-text">
        <SelectValue placeholder="Match" />
      </SelectTrigger>
      <SelectContent className="bg-brand-sidebar border-brand-gold/40 max-h-72 overflow-y-auto">
        {matches.map(m => (
          <SelectItem key={m.match_id} value={String(m.match_id)}
            className="text-brand-text focus:bg-brand-gold/20 focus:text-brand-gold">
            {m.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

- [ ] **Step 3 : Créer `frontend/src/components/selectors/PlayerSelect.tsx`**

```tsx
"use client";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Props { players: string[]; onSelect: (p: string) => void; }

export default function PlayerSelect({ players, onSelect }: Props) {
  return (
    <Select onValueChange={onSelect}>
      <SelectTrigger className="w-full bg-brand-sidebar border-brand-gold/40 text-brand-text">
        <SelectValue placeholder="Joueur" />
      </SelectTrigger>
      <SelectContent className="bg-brand-sidebar border-brand-gold/40 max-h-72 overflow-y-auto">
        {players.map(p => (
          <SelectItem key={p} value={p}
            className="text-brand-text focus:bg-brand-gold/20 focus:text-brand-gold">
            {p}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

- [ ] **Step 4 : Créer `frontend/src/components/analytics/KpiGrid.tsx`**

```tsx
interface KpiItem { label: string; value: string | number; }
interface Props { kpis: KpiItem[]; }

export default function KpiGrid({ kpis }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {kpis.map(({ label, value }) => (
        <div key={label}
          className="bg-brand-sidebar border border-brand-gold/40 rounded-lg p-3 text-center">
          <p className="text-brand-gold text-xs font-semibold uppercase tracking-wide mb-1">
            {label}
          </p>
          <p className="text-white text-xl font-bold">{value}</p>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5 : Créer `frontend/src/components/analytics/PitchImage.tsx`**

```tsx
interface Props { b64: string; alt?: string; }

export default function PitchImage({ b64, alt = "Figure analytique" }: Props) {
  if (!b64) return <div className="h-64 bg-brand-sidebar rounded-lg animate-pulse" />;
  return (
    <img
      src={`data:image/png;base64,${b64}`}
      alt={alt}
      className="w-full rounded-lg border border-brand-gold/20"
    />
  );
}
```

- [ ] **Step 6 : Commit**

```bash
git add frontend/src/components/
git commit -m "feat(frontend): composants sélecteurs et analytics réutilisables"
```

---

## Task 10 : Pages frontend — Profil et Heatmap

**Files:**
- Create: `frontend/src/app/profil/page.tsx`
- Create: `frontend/src/app/heatmap/page.tsx`

- [ ] **Step 1 : Créer `frontend/src/app/profil/page.tsx`**

```tsx
"use client";
import { useState } from "react";
import CompetitionSelect from "@/components/selectors/CompetitionSelect";
import MatchSelect from "@/components/selectors/MatchSelect";
import PlayerSelect from "@/components/selectors/PlayerSelect";
import KpiGrid from "@/components/analytics/KpiGrid";
import PitchImage from "@/components/analytics/PitchImage";
import { api } from "@/lib/api";
import type { Competition, Match, PlayerMetrics } from "@/lib/types";

export default function ProfilPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<PlayerMetrics | null>(null);
  const [summary, setSummary] = useState("");
  const [radarB64, setRadarB64] = useState("");
  const [loading, setLoading] = useState(false);

  async function onCompSelect(comp: Competition) {
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches);
  }

  async function onMatchSelect(m: Match) {
    const d = await api.players(m.match_id);
    setPlayers(d.players);
  }

  async function onPlayerSelect(player: string) {
    const matchId = matches.find(() => true)?.match_id;
    if (!matchId) return;
    setLoading(true);
    const [statsD, radarD] = await Promise.all([
      api.playerStats(matchId, player),
      api.radar(matchId, player),
    ]);
    setMetrics(statsD.metrics);
    setSummary(statsD.summary);
    setRadarB64(radarD.image_b64);
    setLoading(false);
  }

  const kpis = metrics ? [
    { label: "Minutes", value: metrics.minutes },
    { label: "Buts", value: metrics.goals },
    { label: "Passes déc.", value: metrics.assists },
    { label: "Passes", value: metrics.passes },
    { label: "% Passes", value: `${metrics.pass_completion?.toFixed(1)}%` },
    { label: "Pressings", value: metrics.pressures },
    { label: "xG", value: metrics.xg?.toFixed(2) },
    { label: "Passes prog.", value: metrics.progressive_passes },
    { label: "Actions déf.", value: metrics.defensive_actions },
    { label: "Duels gagnés", value: `${metrics.duels_won}/${metrics.duels}` },
  ] : [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-gold">Profil Joueur</h1>
        <p className="text-brand-muted text-sm">Analyse individuelle complète</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} />
        <PlayerSelect players={players} onSelect={onPlayerSelect} />
      </div>

      {loading && <p className="text-brand-muted animate-pulse">Chargement...</p>}

      {metrics && (
        <>
          <KpiGrid kpis={kpis} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-brand-gold font-semibold mb-3">Radar Tactique</h2>
              <PitchImage b64={radarB64} alt="Radar tactique" />
            </div>
            <div>
              <h2 className="text-brand-gold font-semibold mb-3">Résumé Tactique</h2>
              <div className="bg-brand-sidebar rounded-lg p-4 text-sm text-brand-text whitespace-pre-line border border-brand-gold/20">
                {summary}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 2 : Créer `frontend/src/app/heatmap/page.tsx`** (structure identique, appelle `api.heatmap()`)

```tsx
"use client";
import { useState } from "react";
import CompetitionSelect from "@/components/selectors/CompetitionSelect";
import MatchSelect from "@/components/selectors/MatchSelect";
import PlayerSelect from "@/components/selectors/PlayerSelect";
import PitchImage from "@/components/analytics/PitchImage";
import { api } from "@/lib/api";
import type { Competition, Match } from "@/lib/types";

const ACTION_OPTIONS = [
  { value: "all", label: "Toutes actions" },
  { value: "Pass", label: "Passes" },
  { value: "Carry", label: "Conduites" },
  { value: "Pressure", label: "Pressings" },
  { value: "Shot", label: "Tirs" },
];

export default function HeatmapPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [action, setAction] = useState("all");
  const [period, setPeriod] = useState("full");
  const [heatmapB64, setHeatmapB64] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadHeatmap(player: string, a: string, p: string) {
    if (!selectedMatch) return;
    setLoading(true);
    const d = await api.heatmap(selectedMatch.match_id, player, a, p);
    setHeatmapB64(d.image_b64);
    setLoading(false);
  }

  async function onCompSelect(comp: Competition) {
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches);
  }

  async function onMatchSelect(m: Match) {
    setSelectedMatch(m);
    const d = await api.players(m.match_id);
    setPlayers(d.players);
  }

  async function onPlayerSelect(player: string) {
    setSelectedPlayer(player);
    await loadHeatmap(player, action, period);
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-gold">Heatmap & Zones</h1>
        <p className="text-brand-muted text-sm">Zones d'activité sur le terrain</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} />
        <PlayerSelect players={players} onSelect={onPlayerSelect} />
      </div>
      {selectedPlayer && (
        <div className="flex gap-4 flex-wrap">
          <div className="flex gap-2">
            {["full", "1", "2"].map(p => (
              <button key={p}
                onClick={() => { setPeriod(p); loadHeatmap(selectedPlayer, action, p); }}
                className={`px-3 py-1 rounded text-sm border transition-colors
                  ${period === p ? "bg-brand-gold text-brand-bg border-brand-gold"
                                 : "border-brand-gold/40 text-brand-muted hover:border-brand-gold"}`}>
                {p === "full" ? "Complet" : `${p}ère mi-temps`}
              </button>
            ))}
          </div>
          <select
            value={action}
            onChange={e => { setAction(e.target.value); loadHeatmap(selectedPlayer, e.target.value, period); }}
            className="bg-brand-sidebar border border-brand-gold/40 text-brand-text rounded px-3 py-1 text-sm">
            {ACTION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      )}
      {loading && <p className="text-brand-muted animate-pulse">Génération...</p>}
      {heatmapB64 && <PitchImage b64={heatmapB64} alt="Heatmap" />}
    </div>
  );
}
```

- [ ] **Step 3 : Commit**

```bash
git add frontend/src/app/profil/ frontend/src/app/heatmap/
git commit -m "feat(frontend): pages Profil Joueur et Heatmap"
```

---

## Task 11 : Pages Match, Rapport PDF et Tactique

Ces trois pages suivent le même pattern que les tasks 9–10. Référence rapide :

- [ ] **`/match/page.tsx`** — appelle `matchSummary`, `shotMap`, `xgTimeline`, `passNetwork`
- [ ] **`/rapport/page.tsx`** — sélecteurs + textarea observations + bouton qui appelle `api.downloadPdf()` et déclenche un `<a>` download
- [ ] **`/tactique/page.tsx`** — sélecteurs + radio style + formations + POST sur `api.tacticalScore()` → affiche score + feedback

Pour le download PDF dans `/rapport/page.tsx` :

```tsx
async function handleDownload() {
  const blob = await api.downloadPdf({
    match_id: selectedMatch!.match_id,
    player_name: selectedPlayer,
    position: "Milieu",
    competition_label: compLabel,
    observations: observations,
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `rapport_${selectedPlayer}_${selectedMatch!.match_id}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
```

- [ ] **Commit après chaque page**

```bash
git commit -m "feat(frontend): page Analyse Match"
git commit -m "feat(frontend): page Rapport PDF avec download"
git commit -m "feat(frontend): page Analyse Tactique"
```

---

## Task 12 : Docker Compose (dev local full-stack)

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1 : Créer `.env.example`**

```env
# Backend
PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 2 : Créer `docker-compose.yml`**

```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

- [ ] **Step 3 : Créer `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 4 : Créer `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
CMD ["npm", "run", "dev"]
```

- [ ] **Step 5 : Tester en local**

```bash
cp .env.example .env
docker-compose up --build
# Backend : http://localhost:8000/docs
# Frontend : http://localhost:3000
```

- [ ] **Step 6 : Commit**

```bash
git add docker-compose.yml .env.example backend/Dockerfile frontend/Dockerfile
git commit -m "feat: docker-compose dev full-stack"
```

---

## Task 13 : Déploiement Railway (backend) + Vercel (frontend)

- [ ] **Step 1 : Déployer le backend sur Railway**

```bash
# Installer Railway CLI
npm install -g @railway/cli
railway login
cd backend
railway init
railway up
# Railway détecte le Dockerfile et déploie automatiquement
# Récupérer l'URL : https://sportanalytics-backend.up.railway.app
```

- [ ] **Step 2 : Configurer la variable d'env sur Vercel**

```bash
# Dans le dashboard Vercel → Settings → Environment Variables
NEXT_PUBLIC_API_URL = https://sportanalytics-backend.up.railway.app
```

- [ ] **Step 3 : Déployer le frontend sur Vercel**

```bash
cd frontend
npx vercel --prod
# L'URL de production est retournée : https://la-soccer-machine.vercel.app
```

- [ ] **Step 4 : Mettre à jour le CORS dans `backend/main.py`**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://la-soccer-machine.vercel.app",  # ← ton URL Vercel réel
    ],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
```

- [ ] **Step 5 : Commit et push final**

```bash
git add backend/main.py
git commit -m "fix(backend): CORS ajusté pour l'URL Vercel de production"
git push origin master
```

---

## Récapitulatif — Effort estimé

| Task | Durée estimée |
|------|---------------|
| 1 — Bootstrap FastAPI | 20 min |
| 2 — Migration services Python | 30 min |
| 3-6 — Routers backend | 45 min |
| 7 — Bootstrap Next.js | 20 min |
| 8-9 — Layout + composants | 30 min |
| 10-11 — 5 pages frontend | 60 min |
| 12 — Docker Compose | 15 min |
| 13 — Déploiement | 20 min |
| **Total** | **~4h** |

## Décision de déploiement alternatif

Si Railway + Vercel est trop complexe au départ, une alternative simple :

```bash
# Tout en local ou sur un VPS unique
# Backend sur port 8000, frontend sur port 3000
# Reverse proxy nginx pour pointer un domaine unique
```

---

---

## Stratégie données — StatsBomb + FBref + Vidéo

### Pourquoi StatsBomb open data ne suffit pas en prod

StatsBomb open data = matchs historiques (La Liga 2014–2020, quelques Euros/CM). Parfait pour :
- Développement et tests
- Benchmarks de référence
- Entraînement de modèles et agents IA

Pour une utilisation pro en temps réel, il faut des données récentes.

### Architecture données recommandée

| Source | Route FastAPI | Usage | Fraîcheur | Coût |
|--------|--------------|-------|-----------|------|
| StatsBomb open | `/competitions`, `/players`, `/match` | Dev, training, benchmarks | Historique | Gratuit |
| **FBref** (soccerdata) | `/fbref/*` | Stats joueurs/équipes saison en cours | ~hebdomadaire | Gratuit (scraping) |
| StatsBomb API pro | À ajouter | Events data haute qualité récente | Live | Abonnement |
| Vidéo upload | `/video/analyze` | Analyse contextuelle du club | Temps réel | Calcul local |

### Roadmap Vidéo — Analyse Vidéo Upload (Phase 2)

La page `/video` est un placeholder. Voici l'architecture cible :

**Backend — `backend/routers/video.py`:**
```python
# Upload MP4/MOV → extraction frames → analyse OpenCV → overlay → retour stats
POST /video/analyze
  → multipart/form-data: file + params (player_tracking, zones, speed)
  → Réponse: { frames_b64: str[], stats: VideoStats, overlay_url: str }
```

**Services Python à ajouter:**
```
backend/services/video_analyzer.py
  - extract_frames(video_bytes) → list[np.ndarray]
  - detect_players(frames) → list[BoundingBox]  # OpenCV ou YOLOv8
  - compute_speed(positions, fps) → list[float]
  - draw_trajectory_overlay(frame, positions) → np.ndarray
  - draw_zone_overlay(frame, heatmap_data) → np.ndarray
```

**Dépendances supplémentaires:**
```
opencv-python-headless>=4.9
ultralytics>=8.0  # YOLOv8 pour player detection (optionnel)
```

**Frontend — `src/app/video/page.tsx` (à compléter):**
```tsx
// Zone de drag & drop → upload → progress → affichage frames annotées
// Contrôles: play/pause, toggle overlays (vitesse, trajectoire, zones)
// Export: download frames annotées + rapport JSON stats
```

### FBref — Limitations à connaître

1. **Rate limiting** : FBref limite les requêtes — `soccerdata` gère du cache local automatiquement dans `~/.cache/soccerdata/`
2. **Premier chargement lent** : ~10-30s pour scraper une saison complète
3. **Colonnes variables** : Les noms de colonnes FBref changent selon les saisons — le router `/fbref` filtre sur les colonnes connues avec `if c in df.columns`
4. **Pas de données events** : FBref donne des stats agrégées (par saison/match), pas les events ball-by-ball comme StatsBomb

### Fusion StatsBomb + FBref (idée agent IA)

Un agent futur pourrait :
1. Charger le profil FBref d'un joueur (stats saison en cours) 
2. Trouver des matchs StatsBomb historiques du même joueur ou de joueurs au profil similaire
3. Croiser les deux pour générer un rapport enrichi : "Ce joueur a un profil FBref similaire à X (StatsBomb), voici les patterns tactiques historiques"

---

> Plan complet et sauvegardé dans `docs/superpowers/plans/2026-06-01-saas-migration.md`
