"""xG timeline and match events timeline."""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

PITCH_BG = "#0f1f14"
GOLD = "#d4a017"
GREEN = "#1a4d2e"
TEXT = "#e8e8e8"


def generate_xg_timeline(events: pd.DataFrame, home_team: str, away_team: str) -> plt.Figure:
    """Cumulative xG timeline for both teams."""
    shots = events[events["type"] == "Shot"].copy() if "type" in events.columns else pd.DataFrame()

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(PITCH_BG)
    ax.set_facecolor(PITCH_BG)

    if shots.empty or "shot_statsbomb_xg" not in shots.columns:
        ax.text(0.5, 0.5, "Données xG non disponibles", ha="center", va="center",
                color=GOLD, transform=ax.transAxes, fontsize=12)
        return fig

    shots = shots.sort_values("minute")

    for team, color in [(home_team, GOLD), (away_team, "#4fc3f7")]:
        t_shots = shots[shots["team"] == team].copy()
        if t_shots.empty:
            continue
        minutes = [0] + t_shots["minute"].tolist() + [90]
        xg_vals = [0.0] + t_shots["shot_statsbomb_xg"].cumsum().tolist()
        xg_vals += [xg_vals[-1]]
        ax.step(minutes, xg_vals, color=color, linewidth=2.5, label=team, where="post")
        ax.fill_between(minutes, xg_vals, step="post", color=color, alpha=0.12)

        goals = t_shots[t_shots.get("shot_outcome", pd.Series()) == "Goal"] \
            if "shot_outcome" in t_shots.columns else pd.DataFrame()
        if not goals.empty:
            for _, row in goals.iterrows():
                xg_at_goal = t_shots[t_shots["minute"] <= row["minute"]]["shot_statsbomb_xg"].sum()
                ax.scatter(row["minute"], xg_at_goal, color=color, s=120, zorder=5,
                           edgecolors="white", linewidths=1)

    ax.set_xlabel("Minute", color=TEXT, fontsize=10)
    ax.set_ylabel("xG cumulé", color=TEXT, fontsize=10)
    ax.set_title("Timeline xG", color=GOLD, fontsize=13)
    ax.tick_params(colors=TEXT)
    ax.spines["bottom"].set_color(GOLD)
    ax.spines["left"].set_color(GOLD)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.legend(facecolor=GREEN, edgecolor=GOLD, labelcolor=TEXT, fontsize=9)
    ax.axvline(45, color=TEXT, linestyle="--", alpha=0.3, linewidth=1)
    ax.set_xlim(0, shots["minute"].max() + 5)

    return fig


def generate_events_timeline(events: pd.DataFrame) -> plt.Figure:
    """Compact horizontal timeline of key events (goals, cards, subs)."""
    KEY_TYPES = {"Goal": ("⚽", "#ffeb3b"), "Yellow Card": ("🟨", "#ffd700"),
                 "Red Card": ("🟥", "#ef5350"), "Substitution": ("🔄", "#90caf9")}

    if events.empty or "type" not in events.columns:
        fig, ax = plt.subplots(figsize=(10, 2))
        fig.patch.set_facecolor(PITCH_BG)
        ax.set_facecolor(PITCH_BG)
        ax.axis("off")
        return fig

    key_events = []
    for etype, (symbol, color) in KEY_TYPES.items():
        subset = events[events["type"] == etype] if etype != "Goal" else \
            events[(events["type"] == "Shot") & (events.get("shot_outcome", pd.Series()) == "Goal")] \
            if "shot_outcome" in events.columns else pd.DataFrame()
        if not subset.empty:
            for _, row in subset.iterrows():
                player = row.get("player", "")
                minute = row.get("minute", 0)
                team = row.get("team", "")
                key_events.append({"minute": minute, "symbol": symbol,
                                   "color": color, "player": player, "team": team})

    fig, ax = plt.subplots(figsize=(10, 1.8))
    fig.patch.set_facecolor(PITCH_BG)
    ax.set_facecolor(PITCH_BG)
    ax.set_xlim(0, 95)
    ax.set_ylim(-0.5, 0.5)
    ax.axhline(0, color=GOLD, linewidth=2, alpha=0.5)
    ax.axvline(45, color=TEXT, linestyle="--", alpha=0.3)

    for ev in key_events:
        ax.scatter(ev["minute"], 0, color=ev["color"], s=200, zorder=5)
        ax.text(ev["minute"], 0.25, ev["symbol"], ha="center", va="bottom", fontsize=10)
        name = ev["player"].split()[-1] if ev["player"] else ""
        ax.text(ev["minute"], -0.3, f"{ev['minute']}' {name}",
                ha="center", va="top", color=TEXT, fontsize=7, rotation=30)

    ax.set_xlabel("Minute", color=TEXT, fontsize=9)
    ax.set_title("Événements clés", color=GOLD, fontsize=11)
    ax.tick_params(colors=TEXT)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_yticks([])

    return fig
