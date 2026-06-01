"""
Tactical metrics calculations for la soccer Machine analytics.
All functions take a StatsBomb events DataFrame and return numeric values.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Coordinate helpers ────────────────────────────────────────────────────────

def _extract_xy(df: pd.DataFrame, col: str = "location") -> pd.DataFrame:
    """Add x/y columns from a list-valued location column if not already present."""
    out = df.copy()
    x_col = f"{col}_x" if col != "location" else "location_x"
    y_col = f"{col}_y" if col != "location" else "location_y"
    if x_col not in out.columns and col in out.columns:
        out[x_col] = out[col].apply(
            lambda v: v[0] if isinstance(v, (list, tuple)) and len(v) >= 2 else np.nan
        )
        out[y_col] = out[col].apply(
            lambda v: v[1] if isinstance(v, (list, tuple)) and len(v) >= 2 else np.nan
        )
    return out


# StatsBomb pitch: 120 x 80
_PITCH_LENGTH = 120.0
_PITCH_WIDTH = 80.0


def _is_progressive(x_start: float, y_start: float, x_end: float, y_end: float) -> bool:
    """
    A pass / carry is progressive if it moves the ball significantly closer
    to the opponent goal (rough StatsBomb definition).
    """
    goal_x = _PITCH_LENGTH
    goal_y = _PITCH_WIDTH / 2
    dist_start = np.sqrt((goal_x - x_start) ** 2 + (goal_y - y_start) ** 2)
    dist_end = np.sqrt((goal_x - x_end) ** 2 + (goal_y - y_end) ** 2)
    # Must reduce distance by at least 25%
    return dist_end < dist_start * 0.75


# ── Pressing ──────────────────────────────────────────────────────────────────

def calculate_pressing_intensity(events: pd.DataFrame, player_name: str) -> float:
    """
    Pressing intensity = pressures / (minutes * normalisation factor).
    Returns pressures-per-90-minutes equivalent normalised to [0, 1].
    """
    if events.empty or "type" not in events.columns:
        return 0.0

    pe = events[events.get("player", pd.Series()) == player_name] if "player" in events.columns else events
    pressures = pe[pe["type"] == "Pressure"]
    n_pressures = len(pressures)

    minutes = int(pe["minute"].max()) if ("minute" in pe.columns and not pe.empty) else 90
    minutes = max(minutes, 1)

    per_90 = n_pressures / minutes * 90
    # Normalise: elite pressing ~25 per 90
    return round(min(1.0, per_90 / 25.0), 3)


# ── Progressive passes ────────────────────────────────────────────────────────

def calculate_progressive_passes(events: pd.DataFrame, player_name: str) -> int:
    """Count passes that advance the ball ≥25% closer to opponent goal."""
    if events.empty or "type" not in events.columns:
        return 0

    df = events.copy()
    if "player" in df.columns:
        df = df[df["player"] == player_name]

    passes = df[df["type"] == "Pass"]
    if passes.empty:
        return 0

    # Flatten locations
    passes = _extract_xy(passes, "location")
    if "pass_end_location_x" not in passes.columns and "pass_end_location" in passes.columns:
        passes["pass_end_location_x"] = passes["pass_end_location"].apply(
            lambda v: v[0] if isinstance(v, (list, tuple)) and len(v) >= 2 else np.nan
        )
        passes["pass_end_location_y"] = passes["pass_end_location"].apply(
            lambda v: v[1] if isinstance(v, (list, tuple)) and len(v) >= 2 else np.nan
        )

    needed = ["location_x", "location_y", "pass_end_location_x", "pass_end_location_y"]
    if not all(c in passes.columns for c in needed):
        return 0

    valid = passes[needed].dropna()
    count = 0
    for _, row in valid.iterrows():
        if _is_progressive(row["location_x"], row["location_y"],
                           row["pass_end_location_x"], row["pass_end_location_y"]):
            count += 1
    return count


# ── Defensive actions ─────────────────────────────────────────────────────────

def calculate_defensive_actions(events: pd.DataFrame, player_name: str) -> int:
    """
    Count defensive actions: tackles, interceptions, clearances, blocks, pressures.
    """
    if events.empty or "type" not in events.columns:
        return 0

    df = events.copy()
    if "player" in df.columns:
        df = df[df["player"] == player_name]

    defensive_types = {"Tackle", "Interception", "Clearance", "Block", "Pressure",
                       "Ball Recovery", "Duel", "Shield"}
    return int((df["type"].isin(defensive_types)).sum())


# ── Position benchmarks ───────────────────────────────────────────────────────

def get_position_benchmarks(events: pd.DataFrame, position: str) -> dict:
    """
    Compute average stats for all players of the same position group in the match.
    Returns a dict matching the keys from aggregate_player_stats().
    """
    if events.empty or "player" not in events.columns:
        return {}

    pos_lower = str(position).lower()

    # Map StatsBomb position names to groups
    def _pos_group(p: str) -> str:
        p = str(p).lower()
        if any(x in p for x in ["forward", "winger", "striker", "centre-forward", "left wing", "right wing", "second striker"]):
            return "Forward"
        if any(x in p for x in ["midfielder", "midfield", "pivot", "attacking mid", "defensive mid", "central mid"]):
            return "Midfielder"
        if any(x in p for x in ["defender", "back", "left back", "right back", "centre back", "sweeper"]):
            return "Defender"
        if "goalkeeper" in p:
            return "Goalkeeper"
        return "Unknown"

    target_group = _pos_group(position)

    # Get position for each player from lineups if available in events
    # We use a fallback: assign groups based on their dominant event locations
    players = events["player"].dropna().unique().tolist()

    from data.loaders.statsbomb_loader import aggregate_player_stats

    all_stats: list[dict] = []
    for player in players:
        s = aggregate_player_stats(events, player)
        if s:
            all_stats.append(s)

    if not all_stats:
        return {}

    keys = all_stats[0].keys()
    averages = {}
    for k in keys:
        vals = [float(s.get(k, 0) or 0) for s in all_stats]
        averages[k] = round(np.mean(vals), 3)

    # Add derived metrics
    averages["progressive_passes"] = round(
        np.mean([calculate_progressive_passes(events, p) for p in players[:10]]), 2
    )
    averages["pressing_intensity"] = round(
        np.mean([calculate_pressing_intensity(events, p) for p in players[:10]]), 3
    )
    averages["defensive_actions"] = round(
        np.mean([calculate_defensive_actions(events, p) for p in players[:10]]), 2
    )

    return averages


# ── Full player metrics dict ──────────────────────────────────────────────────

def build_full_player_metrics(events: pd.DataFrame, player_name: str) -> dict:
    """
    Return a complete metrics dict including derived tactical metrics.
    Merges aggregate_player_stats + pressing / progressive / defensive.
    """
    from data.loaders.statsbomb_loader import aggregate_player_stats

    base = aggregate_player_stats(events, player_name)
    base["progressive_passes"] = calculate_progressive_passes(events, player_name)
    base["pressing_intensity"] = calculate_pressing_intensity(events, player_name)
    base["defensive_actions"] = calculate_defensive_actions(events, player_name)
    return base


# ── Tactical text summary ────────────────────────────────────────────────────

def tactical_summary_text(metrics: dict, player_name: str, position: str = "") -> str:
    """Generate a short French tactical summary from a metrics dict."""
    lines = [f"**Résumé tactique — {player_name}**"]

    if position:
        lines.append(f"*Poste : {position}*")

    press_int = metrics.get("pressing_intensity", 0) or 0
    if press_int >= 0.6:
        lines.append("⚡ Pressing très intense : le joueur récupère le ballon haut.")
    elif press_int >= 0.3:
        lines.append("🔄 Pressing modéré : participation correcte à la récupération collective.")
    else:
        lines.append("⬇️ Faible intensité de pressing dans ce match.")

    prog = metrics.get("progressive_passes", 0) or 0
    passes = metrics.get("passes", 1) or 1
    if prog / passes > 0.25:
        lines.append("🚀 Fort volume de passes progressives — joueur dynamisant verticalement.")
    elif prog > 0:
        lines.append(f"➡️ {prog} passe(s) progressive(s) — contribution à la progression.")

    duels = metrics.get("duels", 1) or 1
    duels_won = metrics.get("duels_won", 0) or 0
    duel_rate = duels_won / duels if duels > 0 else 0
    if duel_rate >= 0.6:
        lines.append(f"💪 Excellent taux de duels gagnés : {duels_won}/{duels} ({duel_rate:.0%}).")
    elif duels > 0:
        lines.append(f"⚔️ Duels : {duels_won}/{duels} gagnés ({duel_rate:.0%}).")

    def_actions = metrics.get("defensive_actions", 0) or 0
    if def_actions >= 10:
        lines.append(f"🛡️ {def_actions} actions défensives — présence défensive marquée.")
    elif def_actions > 0:
        lines.append(f"🛡️ {def_actions} actions défensives.")

    xg = metrics.get("xg", 0) or 0
    goals = metrics.get("goals", 0) or 0
    if xg > 0:
        if goals > xg:
            lines.append(f"🎯 Efficacité au-dessus des attentes : {goals} but(s) pour {xg:.2f} xG.")
        else:
            lines.append(f"⚽ {goals} but(s) pour {xg:.2f} xG.")

    return "\n\n".join(lines)
