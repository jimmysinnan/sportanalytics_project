"""
la soccer Machine — Sport Analytics Dashboard
Main entry point for the Streamlit multi-page app.
"""

import streamlit as st
import pandas as pd
from data.loaders.statsbomb_loader import list_competitions

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="la soccer Machine | Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS / branding ─────────────────────────────────────────────────────
BRAND_CSS = """
<style>
/* ---------- Base ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f1f14;
    color: #e8e8e8;
    font-family: 'Segoe UI', sans-serif;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background-color: #1a4d2e !important;
    border-right: 2px solid #d4a017;
}
[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}
[data-testid="stSidebar"] a:hover {
    color: #d4a017 !important;
}

/* ---------- Headers ---------- */
h1, h2, h3 { color: #d4a017; }
h4, h5, h6 { color: #a8c5b0; }

/* ---------- Selectbox / widgets ---------- */
.stSelectbox label, .stMultiSelect label, .stRadio label { color: #d4a017 !important; }

/* ---------- Metric cards ---------- */
[data-testid="stMetric"] {
    background-color: #1a4d2e;
    border: 1px solid #d4a017;
    border-radius: 8px;
    padding: 10px;
}
[data-testid="stMetricLabel"] { color: #d4a017 !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; }

/* ---------- Dataframe ---------- */
.stDataFrame { border: 1px solid #d4a017; border-radius: 6px; }

/* ---------- Buttons ---------- */
.stButton > button {
    background-color: #d4a017;
    color: #0f1f14;
    font-weight: bold;
    border: none;
    border-radius: 6px;
}
.stButton > button:hover {
    background-color: #b8891b;
    color: #ffffff;
}

/* ---------- Download button ---------- */
.stDownloadButton > button {
    background-color: #1a4d2e;
    color: #d4a017;
    border: 2px solid #d4a017;
    border-radius: 6px;
    font-weight: bold;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab"] {
    color: #a8c5b0;
}
.stTabs [aria-selected="true"] {
    color: #d4a017 !important;
    border-bottom: 2px solid #d4a017;
}

/* ---------- Divider ---------- */
hr { border-color: #d4a017; opacity: 0.3; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 16px 0 8px 0;">
            <span style="font-size:2rem;">⚽</span><br>
            <span style="font-size:1.4rem; font-weight:800; color:#d4a017;
                         letter-spacing:0.05em;">la soccer Machine</span><br>
            <span style="font-size:0.75rem; color:#a8c5b0; letter-spacing:0.15em;">
                SPORT ANALYTICS
            </span>
        </div>
        <hr style="border-color:#d4a017; opacity:0.4; margin:8px 0 16px 0;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Navigate**")
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_Profil_Joueur.py", label="👤 Profil Joueur")
    st.page_link("pages/2_Heatmap_Zones.py", label="🔥 Heatmap & Zones")
    st.page_link("pages/3_Analyse_Match.py", label="📊 Analyse Match")
    st.page_link("pages/4_Rapport_PDF.py", label="📄 Rapport PDF")

    st.markdown("---")
    st.caption("Data: StatsBomb Open Data")
    st.caption("© 2026 la soccer Machine")

# ── Home page ─────────────────────────────────────────────────────────────────
st.title("⚽ la soccer Machine — Tableau de Bord")
st.markdown(
    "<p style='color:#a8c5b0; font-size:1.05rem;'>"
    "Plateforme d'analyse tactique professionnelle pour joueurs et entraîneurs."
    "</p>",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📂 Compétitions", "44+", help="StatsBomb Open Data")
with col2:
    st.metric("🎯 Analyses dispo", "4", help="Pages d'analyse")
with col3:
    st.metric("📈 Métriques", "30+", help="KPIs tactiques calculés")
with col4:
    st.metric("📄 Export", "PDF", help="Rapports personnalisés")

st.markdown("---")

# ── Competitions table ────────────────────────────────────────────────────────
st.subheader("📋 Compétitions disponibles (StatsBomb Open Data)")

with st.spinner("Chargement des compétitions..."):
    try:
        comps = list_competitions()
        if comps is not None and not comps.empty:
            display_cols = [c for c in ["competition_name", "season_name", "country_name", "competition_gender"] if c in comps.columns]
            comps_display = comps[display_cols].drop_duplicates().sort_values(display_cols[0])
            comps_display.columns = [c.replace("_", " ").title() for c in display_cols]
            st.dataframe(comps_display, use_container_width=True, height=420)
        else:
            st.info("Impossible de charger les compétitions. Vérifiez votre connexion.")
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")

st.markdown("---")
st.markdown(
    """
    <div style='display:flex; gap:32px; flex-wrap:wrap;'>
        <div style='background:#1a4d2e; border:1px solid #d4a017; border-radius:10px;
                    padding:20px; flex:1; min-width:200px;'>
            <h4 style='color:#d4a017;'>👤 Profil Joueur</h4>
            <p style='color:#a8c5b0; font-size:0.9rem;'>
                Analyse individuelle complète : radar tactique, métriques de pressing,
                progression, duels. Comparez un joueur à ses pairs de poste.
            </p>
        </div>
        <div style='background:#1a4d2e; border:1px solid #d4a017; border-radius:10px;
                    padding:20px; flex:1; min-width:200px;'>
            <h4 style='color:#d4a017;'>🔥 Heatmap & Zones</h4>
            <p style='color:#a8c5b0; font-size:0.9rem;'>
                Visualisez les zones d'activité d'un joueur sur le terrain.
                Filtrez par période, type d'action et demi-temps.
            </p>
        </div>
        <div style='background:#1a4d2e; border:1px solid #d4a017; border-radius:10px;
                    padding:20px; flex:1; min-width:200px;'>
            <h4 style='color:#d4a017;'>📊 Analyse Match</h4>
            <p style='color:#a8c5b0; font-size:0.9rem;'>
                Vue d'ensemble du match : formations, possession, xG timeline,
                réseau de passes, événements clés.
            </p>
        </div>
        <div style='background:#1a4d2e; border:1px solid #d4a017; border-radius:10px;
                    padding:20px; flex:1; min-width:200px;'>
            <h4 style='color:#d4a017;'>📄 Rapport PDF</h4>
            <p style='color:#a8c5b0; font-size:0.9rem;'>
                Générez un rapport PDF brandé "la soccer Machine" avec stats,
                heatmap, radar et observations tactiques personnalisées.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
