"""
Page 1 — Profil Joueur
Analyse individuelle complète : métriques, radar tactique, résumé.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

from data.loaders.statsbomb_loader import (
    list_competitions, list_matches, load_events,
    get_players_in_match, get_match_label, aggregate_player_stats,
)
from viz.radar import generate_radar, POSITION_METRICS, _position_group
from utils.metrics import (
    calculate_pressing_intensity, calculate_progressive_passes,
    calculate_defensive_actions, get_position_benchmarks, tactical_summary_text,
    build_full_player_metrics,
)

# ── Page config (CSS inherited from app.py via Streamlit multi-page) ──────────
st.set_page_config(page_title="Profil Joueur | la soccer Machine",
                   page_icon="👤", layout="wide")

BRAND_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] { background-color: #0f1f14; color: #e8e8e8; }
[data-testid="stSidebar"] { background-color: #1a4d2e !important; border-right: 2px solid #d4a017; }
[data-testid="stSidebar"] * { color: #e8e8e8 !important; }
h1, h2, h3 { color: #d4a017; }
[data-testid="stMetric"] { background-color: #1a4d2e; border: 1px solid #d4a017; border-radius: 8px; padding: 10px; }
[data-testid="stMetricLabel"] { color: #d4a017 !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; }
.stButton > button { background-color: #d4a017; color: #0f1f14; font-weight: bold; border: none; border-radius: 6px; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

st.title("👤 Profil Joueur")
st.markdown("<p style='color:#a8c5b0;'>Sélectionnez un match StatsBomb pour analyser un joueur.</p>",
            unsafe_allow_html=True)

# ── Sidebar selectors ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 0 4px;'>"
        "<span style='font-size:1.3rem;font-weight:800;color:#d4a017;'>⚽ la soccer Machine</span>"
        "</div><hr style='border-color:#d4a017;opacity:0.4;'>",
        unsafe_allow_html=True,
    )
    st.markdown("**Navigation**")
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_Profil_Joueur.py", label="👤 Profil Joueur")
    st.page_link("pages/2_Heatmap_Zones.py", label="🔥 Heatmap & Zones")
    st.page_link("pages/3_Analyse_Match.py", label="📊 Analyse Match")
    st.page_link("pages/4_Rapport_PDF.py", label="📄 Rapport PDF")

# ── Competition selector ──────────────────────────────────────────────────────
with st.spinner("Chargement des compétitions..."):
    comps = list_competitions()

if comps.empty:
    st.error("Impossible de charger les compétitions StatsBomb.")
    st.stop()

comp_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in comps.iterrows()
}
comp_label = st.selectbox("Compétition / Saison", list(comp_options.keys()), key="comp_profil")
comp_id, season_id = comp_options[comp_label]

# ── Match selector ────────────────────────────────────────────────────────────
with st.spinner("Chargement des matchs..."):
    matches = list_matches(comp_id, season_id)

if matches.empty:
    st.warning("Aucun match disponible pour cette compétition/saison.")
    st.stop()

match_labels = {get_match_label(row): row["match_id"] for _, row in matches.iterrows()}
match_label = st.selectbox("Match", list(match_labels.keys()), key="match_profil")
match_id = match_labels[match_label]

# ── Load events ───────────────────────────────────────────────────────────────
with st.spinner("Chargement des événements..."):
    events = load_events(match_id)

if events.empty:
    st.warning("Impossible de charger les événements du match.")
    st.stop()

# ── Player selector ───────────────────────────────────────────────────────────
players = get_players_in_match(events)
if not players:
    st.warning("Aucun joueur trouvé dans les événements.")
    st.stop()

player_name = st.selectbox("Joueur", players, key="player_profil")

# ── Position selector ─────────────────────────────────────────────────────────
# Try to infer position from lineups column if available
detected_position = "Midfielder"
if "position" in events.columns:
    pos_series = events[events["player"] == player_name]["position"].dropna()
    if not pos_series.empty:
        detected_position = pos_series.iloc[0]

position_groups = ["Attaquant", "Milieu", "Défenseur", "Gardien"]
# Map detected to French group
_grp_map = {"Forward": "Attaquant", "Midfielder": "Milieu",
            "Defender": "Défenseur", "Goalkeeper": "Gardien"}
default_group = _grp_map.get(_position_group(detected_position), "Milieu")
position = st.selectbox("Poste", position_groups,
                         index=position_groups.index(default_group), key="pos_profil")

# ── Compute metrics ───────────────────────────────────────────────────────────
with st.spinner("Calcul des métriques..."):
    metrics = build_full_player_metrics(events, player_name)

if not metrics:
    st.warning("Aucune donnée disponible pour ce joueur.")
    st.stop()

# ── KPI metrics row ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader(f"📊 Statistiques — {player_name}")

cols = st.columns(5)
kpis = [
    ("⏱️ Minutes", metrics.get("minutes", 0), ""),
    ("⚽ Buts", metrics.get("goals", 0), ""),
    ("🎯 Passes déc.", metrics.get("assists", 0), ""),
    ("🎪 Passes", metrics.get("passes", 0), ""),
    ("% Passes réussies", f"{metrics.get('pass_completion', 0):.1f}%", ""),
]
for col, (label, val, help_txt) in zip(cols, kpis):
    col.metric(label, val)

cols2 = st.columns(5)
kpis2 = [
    ("🔥 Pressings", metrics.get("pressures", 0), ""),
    ("⚔️ Duels gagnés", f"{metrics.get('duels_won', 0)}/{metrics.get('duels', 0)}", ""),
    ("🚀 Passes prog.", metrics.get("progressive_actions", metrics.get("progressive_passes", 0)), ""),
    ("🛡️ Actions déf.", metrics.get("defensive_actions", 0), ""),
    ("xG", f"{metrics.get('xg', 0.0):.2f}", ""),
]
for col, (label, val, help_txt) in zip(cols2, kpis2):
    col.metric(label, val)

# ── Radar chart ───────────────────────────────────────────────────────────────
st.markdown("---")
col_radar, col_summary = st.columns([1, 1])

with col_radar:
    st.subheader("🕸️ Radar Tactique")
    with st.spinner("Génération du radar..."):
        try:
            # Get benchmark — average of all players in match (fast approximation)
            all_player_stats = [
                aggregate_player_stats(events, p)
                for p in get_players_in_match(events)[:12]  # limit for speed
            ]
            import numpy as np
            bench = {}
            if all_player_stats:
                keys_all = [k for k in all_player_stats[0].keys()] if all_player_stats[0] else []
                for k in keys_all:
                    vals = [float(s.get(k, 0) or 0) for s in all_player_stats]
                    bench[k] = round(np.mean(vals), 2)
                bench["progressive_passes"] = round(
                    np.mean([calculate_progressive_passes(events, p)
                             for p in get_players_in_match(events)[:8]]), 2
                )
                bench["pressing_intensity"] = round(
                    np.mean([calculate_pressing_intensity(events, p)
                             for p in get_players_in_match(events)[:8]]), 3
                )
                bench["defensive_actions"] = round(
                    np.mean([calculate_defensive_actions(events, p)
                             for p in get_players_in_match(events)[:8]]), 2
                )

            radar_fig = generate_radar(
                player_stats=metrics,
                player_name=player_name,
                position=detected_position,
                benchmark_stats=bench or None,
            )
            st.pyplot(radar_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur radar : {e}")

with col_summary:
    st.subheader("📝 Résumé Tactique")
    summary = tactical_summary_text(metrics, player_name, detected_position)
    st.markdown(summary)

    st.markdown("---")
    st.markdown("**Détail des métriques avancées**")
    adv_df = pd.DataFrame([
        {"Métrique": "Passes progressives", "Valeur": metrics.get("progressive_passes", 0)},
        {"Métrique": "Intensité pressing", "Valeur": f"{metrics.get('pressing_intensity', 0):.3f}"},
        {"Métrique": "Actions défensives", "Valeur": metrics.get("defensive_actions", 0)},
        {"Métrique": "Dribbles réussis", "Valeur": metrics.get("dribbles_completed", 0)},
        {"Métrique": "Passes clés", "Valeur": metrics.get("key_passes", 0)},
        {"Métrique": "Conduites de balle", "Valeur": metrics.get("carries", 0)},
    ])
    st.dataframe(adv_df, use_container_width=True, hide_index=True)

# ── Full stats expander ───────────────────────────────────────────────────────
with st.expander("📋 Toutes les statistiques brutes"):
    stats_df = pd.DataFrame(
        [{"Métrique": k.replace("_", " ").title(),
          "Valeur": f"{v:.3f}" if isinstance(v, float) else str(v)}
         for k, v in metrics.items()]
    )
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
