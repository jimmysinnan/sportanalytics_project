"""Pitch drawing helpers using mplsoccer."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch, VerticalPitch

PITCH_BG = "#0f1f14"
PITCH_LINE = "#d4a017"
PASS_COLOR = "#4fc3f7"
SHOT_COLOR = "#ef5350"
CARRY_COLOR = "#66bb6a"
PRESS_COLOR = "#ffa726"


def _base_pitch(vertical: bool = False) -> tuple:
    """Return (fig, ax) with branded dark pitch."""
    cls = VerticalPitch if vertical else Pitch
    pitch = cls(
        pitch_type="statsbomb",
        pitch_color=PITCH_BG,
        line_color=PITCH_LINE,
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=(8, 6) if not vertical else (6, 8))
    fig.patch.set_facecolor(PITCH_BG)
    return fig, ax, pitch


def draw_passes(events: pd.DataFrame, player_name: str | None = None) -> plt.Figure:
    df = events[events["type"] == "Pass"].copy() if "type" in events.columns else pd.DataFrame()
    if player_name:
        df = df[df["player"] == player_name]

    fig, ax, pitch = _base_pitch()
    if df.empty:
        ax.set_title("Aucune passe disponible", color=PITCH_LINE)
        return fig

    completed = df[df["pass_outcome"].isna()] if "pass_outcome" in df.columns else df
    incomplete = df[df["pass_outcome"].notna()] if "pass_outcome" in df.columns else pd.DataFrame()

    for subset, color, alpha in [(completed, PASS_COLOR, 0.7), (incomplete, "#ef5350", 0.5)]:
        if not subset.empty and all(c in subset.columns for c in ["location", "pass_end_location"]):
            locs = subset["location"].dropna().tolist()
            ends = subset["pass_end_location"].dropna().tolist()
            min_len = min(len(locs), len(ends))
            if min_len > 0:
                xs = [loc[0] for loc in locs[:min_len]]
                ys = [loc[1] for loc in locs[:min_len]]
                xe = [loc[0] for loc in ends[:min_len]]
                ye = [loc[1] for loc in ends[:min_len]]
                pitch.arrows(xs, ys, xe, ye, ax=ax, color=color, alpha=alpha, width=1.5, headwidth=5)

    title = f"Passes — {player_name}" if player_name else "Passes"
    ax.set_title(title, color=PITCH_LINE, fontsize=12, pad=10)
    return fig


def draw_shots(events: pd.DataFrame, team_name: str | None = None) -> plt.Figure:
    df = events[events["type"] == "Shot"].copy() if "type" in events.columns else pd.DataFrame()
    if team_name:
        df = df[df["team"] == team_name]

    fig, ax, pitch = _base_pitch()
    if df.empty or "location" not in df.columns:
        ax.set_title("Aucun tir disponible", color=PITCH_LINE)
        return fig

    goals = df[df.get("shot_outcome", pd.Series()) == "Goal"] if "shot_outcome" in df.columns else pd.DataFrame()
    non_goals = df[df.get("shot_outcome", pd.Series()) != "Goal"] if "shot_outcome" in df.columns else df

    for subset, color, size, zorder in [
        (non_goals, SHOT_COLOR, 80, 3),
        (goals, "#ffeb3b", 150, 4),
    ]:
        if not subset.empty:
            locs = subset["location"].dropna().tolist()
            if locs:
                xs = [l[0] for l in locs]
                ys = [l[1] for l in locs]
                pitch.scatter(xs, ys, ax=ax, color=color, s=size, zorder=zorder,
                              edgecolors="white", linewidths=0.5, alpha=0.85)

    ax.set_title(f"Tirs — {team_name or 'Équipe'}", color=PITCH_LINE, fontsize=12, pad=10)
    return fig


def draw_carries(events: pd.DataFrame, player_name: str | None = None) -> plt.Figure:
    df = events[events["type"] == "Carry"].copy() if "type" in events.columns else pd.DataFrame()
    if player_name:
        df = df[df["player"] == player_name]

    fig, ax, pitch = _base_pitch()
    if df.empty or "location" not in df.columns or "carry_end_location" not in df.columns:
        ax.set_title("Aucune conduite disponible", color=PITCH_LINE)
        return fig

    locs = df["location"].dropna().tolist()
    ends = df["carry_end_location"].dropna().tolist()
    min_len = min(len(locs), len(ends))
    if min_len > 0:
        xs = [l[0] for l in locs[:min_len]]
        ys = [l[1] for l in locs[:min_len]]
        xe = [l[0] for l in ends[:min_len]]
        ye = [l[1] for l in ends[:min_len]]
        pitch.arrows(xs, ys, xe, ye, ax=ax, color=CARRY_COLOR, alpha=0.6, width=1.2, headwidth=4)

    ax.set_title(f"Conduites — {player_name or ''}", color=PITCH_LINE, fontsize=12, pad=10)
    return fig


def draw_pass_network(events: pd.DataFrame, team_name: str, min_passes: int = 3) -> plt.Figure:
    """Draw a pass network (avg positions + connection lines) for a team."""
    df = events[
        (events.get("type", pd.Series()) == "Pass") &
        (events.get("team", pd.Series()) == team_name)
    ].copy() if "type" in events.columns and "team" in events.columns else pd.DataFrame()

    fig, ax, pitch = _base_pitch()
    if df.empty or "player" not in df.columns or "location" not in df.columns:
        ax.set_title("Réseau de passes indisponible", color=PITCH_LINE)
        return fig

    df["x"] = df["location"].apply(lambda l: l[0] if isinstance(l, list) and len(l) >= 2 else None)
    df["y"] = df["location"].apply(lambda l: l[1] if isinstance(l, list) and len(l) >= 2 else None)
    df = df.dropna(subset=["x", "y"])

    avg_pos = df.groupby("player")[["x", "y"]].mean()
    pass_counts = df.groupby(["player", "pass_recipient"]).size().reset_index(name="count") \
        if "pass_recipient" in df.columns else pd.DataFrame()

    node_sizes = df.groupby("player").size() * 30
    pitch.scatter(avg_pos["x"], avg_pos["y"], ax=ax, s=node_sizes.reindex(avg_pos.index, fill_value=60),
                  color=PRESS_COLOR, edgecolors=PITCH_LINE, linewidths=1.5, zorder=5)

    for _, row in avg_pos.iterrows():
        ax.annotate(row.name.split()[-1], (row["x"], row["y"]),
                    color="white", fontsize=6, ha="center", va="bottom",
                    xytext=(0, 6), textcoords="offset points")

    if not pass_counts.empty:
        for _, row in pass_counts[pass_counts["count"] >= min_passes].iterrows():
            if row["player"] in avg_pos.index and row["pass_recipient"] in avg_pos.index:
                x1, y1 = avg_pos.loc[row["player"], ["x", "y"]]
                x2, y2 = avg_pos.loc[row["pass_recipient"], ["x", "y"]]
                alpha = min(0.8, row["count"] / 15)
                lw = min(4, row["count"] / 5)
                ax.plot([x1, x2], [y1, y2], color=PASS_COLOR, alpha=alpha, linewidth=lw, zorder=3)

    ax.set_title(f"Réseau de passes — {team_name}", color=PITCH_LINE, fontsize=12, pad=10)
    return fig
