"""
Page 4 — Rapport PDF
Génère un rapport PDF brandé "la soccer Machine" pour un joueur / match.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

from data.loaders.statsbomb_loader import (
    list_competitions, list_matches, load_events,
    get_players_in_match, get_match_label, aggregate_player_stats,
)
from viz.heatmap import generate_heatmap
from viz.radar import generate_radar, _position_group
from utils.metrics import (
    build_full_player_metrics, tactical_summary_text,
    calculate_pressing_intensity, calculate_progressive_passes, calculate_defensive_actions,
)

st.set_page_config(page_title="Rapport PDF | la soccer Machine", page_icon="📄", layout="wide")

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
.stDownloadButton > button { background-color: #1a4d2e; color: #d4a017; border: 2px solid #d4a017; border-radius: 6px; font-weight: bold; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

st.title("📄 Générateur de Rapport PDF")
st.markdown("<p style='color:#a8c5b0;'>Générez un rapport tactique professionnel brandé <strong>la soccer Machine</strong>.</p>",
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

# ── Step 1: Selectors ─────────────────────────────────────────────────────────
st.subheader("Étape 1 — Sélectionner le match et le joueur")

with st.spinner("Chargement des compétitions..."):
    comps = list_competitions()

if comps.empty:
    st.error("Impossible de charger les compétitions.")
    st.stop()

comp_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in comps.iterrows()
}

col1, col2 = st.columns(2)
with col1:
    comp_label = st.selectbox("Compétition / Saison", list(comp_options.keys()), key="comp_pdf")
comp_id, season_id = comp_options[comp_label]

with st.spinner("Chargement des matchs..."):
    matches = list_matches(comp_id, season_id)

if matches.empty:
    st.warning("Aucun match disponible.")
    st.stop()

match_labels = {get_match_label(row): row["match_id"] for _, row in matches.iterrows()}
with col2:
    match_label = st.selectbox("Match", list(match_labels.keys()), key="match_pdf")

match_id = match_labels[match_label]
match_row = matches[matches["match_id"] == match_id].iloc[0]

with st.spinner("Chargement des événements..."):
    events = load_events(match_id)

if events.empty:
    st.warning("Impossible de charger les événements.")
    st.stop()

players = get_players_in_match(events)
if not players:
    st.warning("Aucun joueur trouvé.")
    st.stop()

col3, col4 = st.columns(2)
with col3:
    player_name = st.selectbox("Joueur", players, key="player_pdf")
with col4:
    position_options = ["Attaquant", "Milieu", "Défenseur", "Gardien"]
    detected_pos = "Midfielder"
    if "position" in events.columns:
        pos_series = events[events["player"] == player_name]["position"].dropna()
        if not pos_series.empty:
            detected_pos = pos_series.iloc[0]
    _grp_map = {"Forward": "Attaquant", "Midfielder": "Milieu",
                "Defender": "Défenseur", "Goalkeeper": "Gardien"}
    default_pos = _grp_map.get(_position_group(detected_pos), "Milieu")
    position = st.selectbox("Poste", position_options,
                             index=position_options.index(default_pos), key="pos_pdf")

# ── Step 2: Observations text ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Étape 2 — Observations tactiques de l'analyste")

with st.spinner("Calcul des métriques..."):
    metrics = build_full_player_metrics(events, player_name)

# Pre-fill with auto-generated summary
auto_summary = tactical_summary_text(metrics, player_name, detected_pos)
auto_clean = auto_summary.replace("**", "").replace("*", "")

observations = st.text_area(
    "Observations (modifiables)",
    value=auto_clean,
    height=200,
    key="obs_pdf",
    help="Ce texte sera inclus dans le rapport PDF. Modifiez-le selon votre analyse.",
)

# ── Step 3: Preview ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Étape 3 — Aperçu et génération")

col_prev1, col_prev2 = st.columns(2)

with col_prev1:
    st.markdown("**Heatmap**")
    hm_fig = generate_heatmap(events, player_name=player_name, action_type="all", period="full")
    st.pyplot(hm_fig, use_container_width=True)

with col_prev2:
    st.markdown("**Radar Tactique**")
    import numpy as np
    # Quick benchmark
    bench = {}
    sample_players = get_players_in_match(events)[:8]
    all_stats = [aggregate_player_stats(events, p) for p in sample_players]
    valid_stats = [s for s in all_stats if s]
    if valid_stats:
        for k in valid_stats[0].keys():
            vals = [float(s.get(k, 0) or 0) for s in valid_stats]
            bench[k] = round(np.mean(vals), 2)
        bench["progressive_passes"] = round(
            np.mean([calculate_progressive_passes(events, p) for p in sample_players]), 2)
        bench["pressing_intensity"] = round(
            np.mean([calculate_pressing_intensity(events, p) for p in sample_players]), 3)
        bench["defensive_actions"] = round(
            np.mean([calculate_defensive_actions(events, p) for p in sample_players]), 2)

    radar_fig = generate_radar(
        player_stats=metrics,
        player_name=player_name,
        position=detected_pos,
        benchmark_stats=bench or None,
    )
    st.pyplot(radar_fig, use_container_width=True)

# ── Step 4: Generate PDF ──────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Étape 4 — Télécharger le rapport")

if st.button("🖨️ Générer le rapport PDF", key="gen_pdf"):
    with st.spinner("Génération du rapport PDF..."):
        try:
            from reports.pdf_generator import PlayerReport

            match_info = {
                "match": f"{match_row.get('home_team', '')} vs {match_row.get('away_team', '')}",
                "score": f"{match_row.get('home_score', '')}–{match_row.get('away_score', '')}",
                "date": str(match_row.get("match_date", "")),
                "compétition": str(comp_label),
                "poste": position,
            }

            report = PlayerReport()
            report.add_header(player_name, match_info)
            report.add_stats_table(metrics)
            report.add_figure(hm_fig, "Heatmap — Zones d'activité")
            report.add_figure(radar_fig, "Radar Tactique")
            report.add_observations(observations)
            pdf_bytes = report.generate()

            safe_name = player_name.replace(" ", "_")
            filename = f"rapport_{safe_name}_{match_id}.pdf"

            st.success("✅ Rapport généré avec succès !")
            st.download_button(
                label="⬇️ Télécharger le rapport PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key="dl_pdf",
            )
        except ImportError as e:
            st.error(f"fpdf2 n'est pas installé : {e}")
            st.info("Installez fpdf2 : pip install fpdf2")
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")
            import traceback
            with st.expander("Détails de l'erreur"):
                st.code(traceback.format_exc())

# ── Metrics preview ───────────────────────────────────────────────────────────
with st.expander("📊 Aperçu des statistiques du rapport"):
    import pandas as pd
    LABEL_MAP = {
        "minutes": "Minutes jouées", "goals": "Buts", "assists": "Passes décisives",
        "shots": "Tirs", "shots_on_target": "Tirs cadrés", "xg": "xG",
        "passes": "Passes", "pass_completion": "% Passes réussies",
        "key_passes": "Passes clés", "progressive_passes": "Passes progressives",
        "pressures": "Pressings", "pressing_intensity": "Intensité pressing (0-1)",
        "duels": "Duels", "duels_won": "Duels gagnés",
        "defensive_actions": "Actions défensives",
        "dribbles_attempted": "Dribbles tentés", "dribbles_completed": "Dribbles réussis",
        "carries": "Conduites de balle", "ball_receipts": "Réceptions ballon",
    }
    rows = []
    for k, v in metrics.items():
        label = LABEL_MAP.get(k, k.replace("_", " ").title())
        rows.append({"Statistique": label, "Valeur": f"{v:.3f}" if isinstance(v, float) else str(v)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
