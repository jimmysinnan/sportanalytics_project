"""Heatmap generation using mplsoccer."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import VerticalPitch

PITCH_BG = "#0f1f14"
PITCH_LINE = "#d4a017"


def generate_heatmap(
    events: pd.DataFrame,
    player_name: str | None = None,
    action_type: str = "all",
    period: str = "full",
    title: str | None = None,
) -> plt.Figure:
    """
    Generate a heatmap on a vertical pitch.

    Parameters
    ----------
    events : full match events DataFrame
    player_name : filter to one player (None = entire team/match)
    action_type : 'all' | 'Pass' | 'Carry' | 'Pressure' | 'Shot' | 'Dribble'
    period : 'full' | '1' | '2'
    """
    df = events.copy()

    if player_name:
        df = df[df["player"] == player_name] if "player" in df.columns else df

    if period != "full" and "period" in df.columns:
        df = df[df["period"] == int(period)]

    if action_type != "all" and "type" in df.columns:
        df = df[df["type"] == action_type]

    if "location" not in df.columns:
        fig, ax = plt.subplots(figsize=(6, 8))
        fig.patch.set_facecolor(PITCH_BG)
        ax.set_facecolor(PITCH_BG)
        ax.text(0.5, 0.5, "Données de position manquantes",
                ha="center", va="center", color=PITCH_LINE, transform=ax.transAxes)
        return fig

    locs = df["location"].dropna().tolist()
    if not locs:
        fig, ax = plt.subplots(figsize=(6, 8))
        fig.patch.set_facecolor(PITCH_BG)
        ax.set_facecolor(PITCH_BG)
        ax.text(0.5, 0.5, "Aucune donnée pour ce filtre",
                ha="center", va="center", color=PITCH_LINE, transform=ax.transAxes)
        return fig

    xs = np.array([l[0] for l in locs if isinstance(l, list) and len(l) >= 2])
    ys = np.array([l[1] for l in locs if isinstance(l, list) and len(l) >= 2])

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color=PITCH_BG,
        line_color=PITCH_LINE,
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=(6, 8))
    fig.patch.set_facecolor(PITCH_BG)

    if len(xs) >= 5:
        pitch.kdeplot(xs, ys, ax=ax, fill=True, levels=50,
                      cmap="YlOrRd", thresh=0.05, alpha=0.75, zorder=1)
    else:
        pitch.scatter(xs, ys, ax=ax, color="#d4a017", s=80, zorder=3, alpha=0.8)

    period_label = {"full": "Match complet", "1": "1ère mi-temps", "2": "2ème mi-temps"}.get(str(period), "")
    action_label = action_type if action_type != "all" else "Toutes actions"
    default_title = f"{player_name or 'Joueur'} — {action_label} ({period_label})"
    ax.set_title(title or default_title, color=PITCH_LINE, fontsize=11, pad=8)

    return fig


def generate_team_heatmap(events: pd.DataFrame, team_name: str) -> plt.Figure:
    """Heatmap of all player touches for a team."""
    df = events[events["team"] == team_name].copy() if "team" in events.columns else events.copy()
    return generate_heatmap(df, player_name=None, title=f"Activité globale — {team_name}")
