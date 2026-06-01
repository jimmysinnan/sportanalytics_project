"""
Page 2 — Heatmap & Zones
Heatmap de position sur le terrain, filtrée par période et type d'action.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

from data.loaders.statsbomb_loader import (
    list_competitions, list_matches, load_events,
    get_players_in_match, get_match_label,
)
from viz.heatmap import generate_heatmap

st.set_page_config(page_title="Heatmap | la soccer Machine", page_icon="🔥", layout="wide")

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

st.title("🔥 Heatmap & Zones d'Activité")
st.markdown("<p style='color:#a8c5b0;'>Visualisez les zones d'activité d'un joueur sur le terrain.</p>",
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

# ── Competition / Match selectors ─────────────────────────────────────────────
with st.spinner("Chargement des compétitions..."):
    comps = list_competitions()

if comps.empty:
    st.error("Impossible de charger les compétitions.")
    st.stop()

comp_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in comps.iterrows()
}

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    comp_label = st.selectbox("Compétition / Saison", list(comp_options.keys()), key="comp_hm")
comp_id, season_id = comp_options[comp_label]

with st.spinner("Chargement des matchs..."):
    matches = list_matches(comp_id, season_id)

if matches.empty:
    st.warning("Aucun match disponible.")
    st.stop()

match_labels = {get_match_label(row): row["match_id"] for _, row in matches.iterrows()}

with col_sel2:
    match_label = st.selectbox("Match", list(match_labels.keys()), key="match_hm")

match_id = match_labels[match_label]

with st.spinner("Chargement des événements..."):
    events = load_events(match_id)

if events.empty:
    st.warning("Impossible de charger les événements.")
    st.stop()

players = get_players_in_match(events)
if not players:
    st.warning("Aucun joueur trouvé.")
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    player_name = st.selectbox("Joueur", players, key="player_hm")
with col_c2:
    period = st.radio("Période", ["full", "1", "2"],
                      format_func=lambda x: {"full": "Match complet", "1": "1ère mi-temps", "2": "2ème mi-temps"}[x],
                      horizontal=True, key="period_hm")
with col_c3:
    action_types = ["all", "Pass", "Carry", "Pressure", "Shot", "Dribble", "Ball Receipt*"]
    action_labels = {
        "all": "Toutes actions",
        "Pass": "Passes",
        "Carry": "Conduites",
        "Pressure": "Pressings",
        "Shot": "Tirs",
        "Dribble": "Dribbles",
        "Ball Receipt*": "Réceptions",
    }
    action_type = st.selectbox(
        "Type d'action",
        action_types,
        format_func=lambda x: action_labels.get(x, x),
        key="action_hm",
    )

st.markdown("---")

# ── Heatmap display ───────────────────────────────────────────────────────────
col_hm, col_stats = st.columns([2, 1])

with col_hm:
    with st.spinner("Génération de la heatmap..."):
        fig = generate_heatmap(events, player_name=player_name,
                               action_type=action_type, period=period)
    st.pyplot(fig, use_container_width=True)

with col_stats:
    st.subheader("📊 Statistiques de zone")

    # Compute filtered events count
    df_filtered = events.copy()
    if "player" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["player"] == player_name]
    if period != "full" and "period" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["period"] == int(period)]
    if action_type != "all" and "type" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["type"] == action_type]

    st.metric("Actions affichées", len(df_filtered))

    if "location" in df_filtered.columns and not df_filtered.empty:
        import numpy as np
        locs = df_filtered["location"].dropna().tolist()
        xs = [l[0] for l in locs if isinstance(l, list) and len(l) >= 2]
        ys = [l[1] for l in locs if isinstance(l, list) and len(l) >= 2]
        if xs:
            # Zones: defensive (x<40), middle (40-80), attacking (x>80) on 120m pitch
            def_zone = sum(1 for x in xs if x < 40)
            mid_zone = sum(1 for x in xs if 40 <= x <= 80)
            att_zone = sum(1 for x in xs if x > 80)
            total = len(xs)

            st.markdown("**Répartition par zone**")
            st.metric("🔵 Zone défensive", f"{def_zone} ({def_zone/total*100:.0f}%)" if total else "0")
            st.metric("🟡 Zone milieu", f"{mid_zone} ({mid_zone/total*100:.0f}%)" if total else "0")
            st.metric("🔴 Zone offensive", f"{att_zone} ({att_zone/total*100:.0f}%)" if total else "0")

            avg_x = np.mean(xs)
            avg_y = np.mean(ys)
            zone_name = "Défensive" if avg_x < 40 else ("Milieu" if avg_x < 80 else "Offensive")
            st.markdown(f"**Position moyenne** : X={avg_x:.1f}, Y={avg_y:.1f}")
            st.markdown(f"**Zone dominante** : {zone_name}")

    st.markdown("---")
    st.markdown("**Légende du terrain (StatsBomb)**")
    st.markdown(
        """
        - Largeur : 80m (Y: 0→80)
        - Longueur : 120m (X: 0→120)
        - Attaque : vers X=120
        """,
        unsafe_allow_html=False,
    )

# ── Side-by-side halves comparison ───────────────────────────────────────────
if period == "full":
    st.markdown("---")
    st.subheader("📊 Comparaison 1ère / 2ème mi-temps")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1ère mi-temps**")
        fig1 = generate_heatmap(events, player_name=player_name,
                                action_type=action_type, period="1",
                                title=f"{player_name} — 1ère mi-temps")
        st.pyplot(fig1, use_container_width=True)
    with c2:
        st.markdown("**2ème mi-temps**")
        fig2 = generate_heatmap(events, player_name=player_name,
                                action_type=action_type, period="2",
                                title=f"{player_name} — 2ème mi-temps")
        st.pyplot(fig2, use_container_width=True)
