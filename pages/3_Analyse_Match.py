"""
Page 3 — Analyse Match
Vue d'ensemble : formations, possession, shot map, xG timeline, réseau de passes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np

from data.loaders.statsbomb_loader import (
    list_competitions, list_matches, load_events, load_lineups,
    get_match_label, get_teams_in_match, get_team_events,
)
from viz.pitch import draw_shots, draw_pass_network
from viz.timeline import generate_xg_timeline, generate_events_timeline

st.set_page_config(page_title="Analyse Match | la soccer Machine", page_icon="📊", layout="wide")

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

st.title("📊 Analyse Match")
st.markdown("<p style='color:#a8c5b0;'>Vue d'ensemble complète d'un match : stats, xG, réseaux de passes.</p>",
            unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 0 4px;'>"
        "<span style='font-size:1.3rem;font-weight:800;color:#d4a017;'>⚽ la soccer Machine</span>"
        "</div><hr style='border-color:#d4a017;opacity:0.4;'>",
        unsafe_allow_html=True,
    )
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_Profil_Joueur.py", label="👤 Profil Joueur")
    st.page_link("pages/2_Heatmap_Zones.py", label="🔥 Heatmap & Zones")
    st.page_link("pages/3_Analyse_Match.py", label="📊 Analyse Match")
    st.page_link("pages/4_Rapport_PDF.py", label="📄 Rapport PDF")

# ── Selectors ─────────────────────────────────────────────────────────────────
with st.spinner("Chargement..."):
    comps = list_competitions()

if comps.empty:
    st.error("Impossible de charger les compétitions.")
    st.stop()

comp_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in comps.iterrows()
}

col_s1, col_s2 = st.columns(2)
with col_s1:
    comp_label = st.selectbox("Compétition / Saison", list(comp_options.keys()), key="comp_am")
comp_id, season_id = comp_options[comp_label]

with st.spinner("Chargement des matchs..."):
    matches = list_matches(comp_id, season_id)

if matches.empty:
    st.warning("Aucun match disponible.")
    st.stop()

match_labels = {get_match_label(row): row["match_id"] for _, row in matches.iterrows()}
with col_s2:
    match_label = st.selectbox("Match", list(match_labels.keys()), key="match_am")

match_id = match_labels[match_label]

# Find match row
match_row = matches[matches["match_id"] == match_id].iloc[0]
home_team = match_row.get("home_team", "Domicile")
away_team = match_row.get("away_team", "Extérieur")
home_score = match_row.get("home_score", "?")
away_score = match_row.get("away_score", "?")

with st.spinner("Chargement des événements..."):
    events = load_events(match_id)

if events.empty:
    st.warning("Impossible de charger les événements.")
    st.stop()

teams = get_teams_in_match(events)
if len(teams) < 2:
    home_team_actual = teams[0] if teams else home_team
    away_team_actual = away_team
else:
    home_team_actual, away_team_actual = teams[0], teams[1]

# ── Match header ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""
    <div style='background:#1a4d2e;border:1px solid #d4a017;border-radius:12px;
                padding:20px;text-align:center;margin-bottom:16px;'>
        <span style='font-size:1.2rem;color:#a8c5b0;'>{match_row.get('match_date','')}</span><br>
        <span style='font-size:2rem;font-weight:bold;color:#ffffff;'>{home_team}</span>
        <span style='font-size:2.5rem;color:#d4a017;font-weight:900;'>&nbsp;{home_score} — {away_score}&nbsp;</span>
        <span style='font-size:2rem;font-weight:bold;color:#ffffff;'>{away_team}</span><br>
        <span style='font-size:0.85rem;color:#a8c5b0;'>
            {match_row.get('competition', '')} &nbsp;|&nbsp; {match_row.get('stadium', '')}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Possession & basic stats ──────────────────────────────────────────────────
home_events = events[events["team"] == home_team_actual] if "team" in events.columns else pd.DataFrame()
away_events = events[events["team"] == away_team_actual] if "team" in events.columns else pd.DataFrame()

total_events = len(home_events) + len(away_events)
home_poss = round(len(home_events) / total_events * 100, 1) if total_events > 0 else 50.0
away_poss = round(100 - home_poss, 1)

def _count_type(df, t):
    return int((df["type"] == t).sum()) if "type" in df.columns else 0

home_shots = _count_type(home_events, "Shot")
away_shots = _count_type(away_events, "Shot")
home_passes = _count_type(home_events, "Pass")
away_passes = _count_type(away_events, "Pass")

if "shot_statsbomb_xg" in events.columns and "type" in events.columns:
    home_xg = round(events[(events["team"] == home_team_actual) & (events["type"] == "Shot")]["shot_statsbomb_xg"].sum(), 2)
    away_xg = round(events[(events["team"] == away_team_actual) & (events["type"] == "Shot")]["shot_statsbomb_xg"].sum(), 2)
else:
    home_xg, away_xg = 0.0, 0.0

# Stats comparison table
st.subheader("📈 Statistiques comparatives")
stats_cols = st.columns(5)
stat_rows = [
    ("Possession", f"{home_poss}%", f"{away_poss}%"),
    ("Tirs", home_shots, away_shots),
    ("Passes", home_passes, away_passes),
    ("xG", home_xg, away_xg),
]
for col, (label, h_val, a_val) in zip(stats_cols[:4], stat_rows):
    col.metric(f"🏠 {label}", h_val, delta=f"✈️ {a_val}", delta_color="off")

# Possession bar
st.markdown(
    f"""
    <div style='margin:10px 0;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <span style='color:#d4a017;font-weight:bold;min-width:80px;'>{home_team_actual[:15]}</span>
            <div style='flex:1;background:#1a4d2e;border-radius:4px;overflow:hidden;height:18px;'>
                <div style='width:{home_poss}%;background:#d4a017;height:100%;transition:width 0.5s;'></div>
            </div>
            <span style='color:#4fc3f7;font-weight:bold;min-width:80px;text-align:right;'>{away_team_actual[:15]}</span>
        </div>
        <div style='display:flex;justify-content:space-between;color:#a8c5b0;font-size:0.8rem;margin-top:2px;'>
            <span>{home_poss}%</span><span>Possession</span><span>{away_poss}%</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["⚽ Shot Map", "📈 xG Timeline", "🕸️ Réseau de passes", "📋 Événements clés"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{home_team_actual}**")
        fig_shots_h = draw_shots(events, team_name=home_team_actual)
        st.pyplot(fig_shots_h, use_container_width=True)
    with c2:
        st.markdown(f"**{away_team_actual}**")
        fig_shots_a = draw_shots(events, team_name=away_team_actual)
        st.pyplot(fig_shots_a, use_container_width=True)

with tab2:
    fig_xg = generate_xg_timeline(events, home_team_actual, away_team_actual)
    st.pyplot(fig_xg, use_container_width=True)

    # Shot list table
    if "type" in events.columns:
        shots_df = events[events["type"] == "Shot"].copy()
        display_cols = [c for c in ["minute", "team", "player", "shot_outcome", "shot_statsbomb_xg",
                                     "shot_technique", "shot_body_part"] if c in shots_df.columns]
        if display_cols:
            shots_df = shots_df[display_cols].sort_values("minute") if "minute" in display_cols else shots_df[display_cols]
            shots_df.columns = [c.replace("shot_", "").replace("_", " ").title() for c in display_cols]
            st.dataframe(shots_df, use_container_width=True, hide_index=True)

with tab3:
    selected_team = st.radio(
        "Équipe", [home_team_actual, away_team_actual],
        horizontal=True, key="team_network"
    )
    with st.spinner("Génération du réseau de passes..."):
        fig_network = draw_pass_network(events, selected_team)
    st.pyplot(fig_network, use_container_width=True)

with tab4:
    fig_timeline = generate_events_timeline(events)
    st.pyplot(fig_timeline, use_container_width=True)

    # Key events table
    if "type" in events.columns:
        key_types = ["Shot", "Substitution", "Yellow Card", "Red Card", "Foul Committed"]
        key_df = events[events["type"].isin(key_types)].copy()
        if not key_df.empty:
            show_cols = [c for c in ["minute", "second", "team", "player", "type",
                                      "shot_outcome", "foul_committed_card"] if c in key_df.columns]
            key_df = key_df[show_cols].sort_values("minute") if "minute" in show_cols else key_df[show_cols]
            # Filter to goals + cards + subs
            goal_mask = (key_df.get("type") == "Shot") & (key_df.get("shot_outcome") == "Goal") if "shot_outcome" in key_df.columns else pd.Series(False, index=key_df.index)
            non_shot = key_df["type"] != "Shot" if "type" in key_df.columns else pd.Series(True, index=key_df.index)
            key_df = key_df[non_shot | (goal_mask if isinstance(goal_mask, pd.Series) else pd.Series(False, index=key_df.index))]
            key_df.columns = [c.replace("_", " ").title() for c in key_df.columns]
            st.dataframe(key_df, use_container_width=True, hide_index=True)

# ── Lineups ───────────────────────────────────────────────────────────────────
with st.expander("📋 Compositions des équipes"):
    with st.spinner("Chargement des compositions..."):
        lineups = load_lineups(match_id)

    if lineups:
        lc1, lc2 = st.columns(2)
        for col, team_name in zip([lc1, lc2], list(lineups.keys())[:2]):
            with col:
                st.markdown(f"**{team_name}**")
                lu_df = lineups[team_name]
                if not lu_df.empty:
                    show_lu = [c for c in ["player_name", "player_nickname", "jersey_number",
                                            "country"] if c in lu_df.columns]
                    if show_lu:
                        st.dataframe(lu_df[show_lu], use_container_width=True, hide_index=True)
    else:
        st.info("Compositions non disponibles pour ce match.")
