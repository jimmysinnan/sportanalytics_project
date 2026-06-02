"""Radar chart for player tactical profile using mplsoccer."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PITCH_BG = "#0f1f14"
GOLD = "#d4a017"
GREEN = "#1a4d2e"
TEXT = "#e8e8e8"


# Metrics by position group
POSITION_METRICS: dict[str, list[tuple[str, str]]] = {
    "Attaquant": [
        ("goals", "Buts"),
        ("shots", "Tirs"),
        ("xg", "xG"),
        ("dribbles_completed", "Dribbles réussis"),
        ("key_passes", "Passes décisives"),
        ("pressures", "Pressing"),
    ],
    "Milieu": [
        ("passes", "Passes"),
        ("pass_completion", "% passes"),
        ("key_passes", "Passes clés"),
        ("carries", "Conduites"),
        ("pressures", "Pressing"),
        ("duels_won", "Duels gagnés"),
    ],
    "Défenseur": [
        ("duels", "Duels"),
        ("duels_won", "Duels gagnés"),
        ("pressures", "Pressing"),
        ("carries", "Conduites"),
        ("passes", "Passes"),
        ("pass_completion", "% passes"),
    ],
    "Gardien": [
        ("passes", "Passes"),
        ("pass_completion", "% passes"),
        ("duels", "Duels"),
        ("pressures", "Pressing"),
        ("carries", "Conduites"),
        ("ball_receipts", "Réceptions"),
    ],
}


_SB_POSITION_MAP = {
    "Goalkeeper": "Gardien",
    "Center Back": "Défenseur", "Left Center Back": "Défenseur", "Right Center Back": "Défenseur",
    "Left Back": "Défenseur", "Right Back": "Défenseur",
    "Left Wing Back": "Défenseur", "Right Wing Back": "Défenseur",
    "Defensive Midfield": "Milieu", "Left Defensive Midfield": "Milieu", "Right Defensive Midfield": "Milieu",
    "Center Midfield": "Milieu", "Left Center Midfield": "Milieu", "Right Center Midfield": "Milieu",
    "Left Midfield": "Milieu", "Right Midfield": "Milieu",
    "Attacking Midfield": "Milieu", "Left Attacking Midfield": "Milieu", "Right Attacking Midfield": "Milieu",
    "Left Wing": "Attaquant", "Right Wing": "Attaquant",
    "Center Forward": "Attaquant", "Left Center Forward": "Attaquant", "Right Center Forward": "Attaquant",
    "Secondary Striker": "Attaquant",
}


def _position_group(sb_position: str) -> str:
    """Map a StatsBomb position string to French position group label."""
    return _SB_POSITION_MAP.get(sb_position, "Milieu")


def _normalize(values: list[float], mins: list[float], maxs: list[float]) -> list[float]:
    result = []
    for v, lo, hi in zip(values, mins, maxs):
        if hi == lo:
            result.append(0.5)
        else:
            result.append(max(0.0, min(1.0, (v - lo) / (hi - lo))))
    return result


def generate_radar(
    player_stats: dict,
    player_name: str,
    position: str = "Milieu",
    benchmark_stats: dict | None = None,
) -> plt.Figure:
    """
    Draw a radar chart comparing a player to a benchmark (position average or None).

    Parameters
    ----------
    player_stats : dict from aggregate_player_stats()
    player_name : display name
    position : 'Attaquant' | 'Milieu' | 'Défenseur' | 'Gardien'
    benchmark_stats : optional dict of benchmark values (position averages)
    """
    metrics = POSITION_METRICS.get(position, POSITION_METRICS["Milieu"])
    keys = [m[0] for m in metrics]
    labels = [m[1] for m in metrics]
    N = len(keys)

    player_vals = [float(player_stats.get(k, 0) or 0) for k in keys]

    if benchmark_stats:
        bench_vals = [float(benchmark_stats.get(k, 0) or 0) for k in keys]
        mins = [min(p, b) * 0.8 for p, b in zip(player_vals, bench_vals)]
        maxs = [max(p, b) * 1.2 + 1e-6 for p, b in zip(player_vals, bench_vals)]
    else:
        mins = [0.0] * N
        maxs = [max(v * 1.2, 1e-6) for v in player_vals]

    player_norm = _normalize(player_vals, mins, maxs)
    bench_norm = _normalize(bench_vals, mins, maxs) if benchmark_stats else None

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles_closed = angles + [angles[0]]
    player_closed = player_norm + [player_norm[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(PITCH_BG)
    ax.set_facecolor(PITCH_BG)

    # Gridlines style
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=TEXT, fontsize=9)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], color="#666", fontsize=7)
    ax.tick_params(colors=TEXT)
    ax.spines["polar"].set_color(GOLD)
    ax.spines["polar"].set_alpha(0.4)
    for gl in ax.yaxis.get_gridlines():
        gl.set_color(GOLD)
        gl.set_alpha(0.15)

    # Benchmark fill
    if bench_norm:
        bench_closed = bench_norm + [bench_norm[0]]
        ax.fill(angles_closed, bench_closed, color="#4fc3f7", alpha=0.15)
        ax.plot(angles_closed, bench_closed, color="#4fc3f7", linewidth=1.5, linestyle="--", alpha=0.7)

    # Player fill
    ax.fill(angles_closed, player_closed, color=GOLD, alpha=0.25)
    ax.plot(angles_closed, player_closed, color=GOLD, linewidth=2.5)
    ax.scatter(angles, player_norm, color=GOLD, s=60, zorder=5)

    # Value annotations
    for angle, val_norm, val_raw in zip(angles, player_norm, player_vals):
        ax.annotate(
            f"{val_raw:.1f}" if isinstance(val_raw, float) and val_raw != int(val_raw) else str(int(val_raw)),
            xy=(angle, val_norm),
            xytext=(0, 10),
            textcoords="offset points",
            color=GOLD,
            fontsize=8,
            ha="center",
        )

    title_parts = [player_name, f"({position})"]
    if benchmark_stats:
        title_parts.append("vs moy. poste")
    ax.set_title(" ".join(title_parts), color=GOLD, fontsize=12, pad=20)

    if benchmark_stats:
        ax.plot([], [], color=GOLD, linewidth=2, label=player_name)
        ax.plot([], [], color="#4fc3f7", linewidth=1.5, linestyle="--", label="Moy. poste")
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
                  facecolor=GREEN, edgecolor=GOLD, labelcolor=TEXT, fontsize=8)

    return fig
