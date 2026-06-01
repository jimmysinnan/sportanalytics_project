"""
Page 5 — Analyse Tactique
Moteur d'analyse tactique générique : calcule le Score de Compatibilité Tactique (0–100)
pour n'importe quel style de jeu (pressing haut, jeu positionnel, contre-attaque, hybride).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from data.loaders.statsbomb_loader import (
    list_competitions,
    list_matches,
    load_events,
    get_players_in_match,
    get_match_label,
)
from engine.tactical_engine import compute_tactical_score, MatchReport

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analyse Tactique | la soccer Machine",
    page_icon="🧭",
    layout="wide",
)

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
.score-badge { font-size: 3rem; font-weight: 900; text-align: center; padding: 20px;
               border-radius: 12px; border: 3px solid; margin: 10px 0; }
.score-green  { color: #2ecc71; border-color: #2ecc71; background-color: rgba(46,204,113,0.08); }
.score-orange { color: #f39c12; border-color: #f39c12; background-color: rgba(243,156,18,0.08); }
.score-red    { color: #e74c3c; border-color: #e74c3c; background-color: rgba(231,76,60,0.08); }
.feedback-item { background-color: #1a4d2e; border-left: 4px solid #d4a017;
                 padding: 10px 16px; margin: 8px 0; border-radius: 0 6px 6px 0; color: #e8e8e8; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
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
    st.page_link("pages/5_Analyse_Tactique.py", label="🧭 Analyse Tactique")

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🧭 Moteur d'Analyse Tactique")
st.markdown(
    "<p style='color:#a8c5b0;'>Évaluez la compatibilité tactique d'un joueur avec n'importe quel "
    "système de jeu — pressing haut, jeu positionnel, contre-attaque ou hybride.</p>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Team style selection
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("① Style de Jeu de l'Équipe")

STYLE_DESCRIPTIONS = {
    "Jeu Positionnel": (
        "positional",
        "Domination territoriale, conservation du ballon, rotations structurées, jeu entre les lignes. "
        "Valorise les passes verticales, la polyvalence et les combinaisons en demi-espaces.",
    ),
    "Pressing Haut": (
        "high-press",
        "Récupération haute du ballon, pressing immédiat après perte (contre-pressing), "
        "haute intensité physique. Valorise la fréquence de pressing, le contre-pressing et la distance.",
    ),
    "Contre-Attaque": (
        "counter",
        "Transition rapide défense→attaque, passes verticales directes, courses en profondeur, "
        "exploitation des espaces. Valorise la verticalité, la distance et les incursions dans les demi-espaces.",
    ),
    "Hybride": (
        "hybrid",
        "Système flexible, mélange d'approches selon le contexte. "
        "Pondération équilibrée entre toutes les dimensions tactiques.",
    ),
}

style_label = st.radio(
    "Choisissez le style tactique à analyser",
    list(STYLE_DESCRIPTIONS.keys()),
    horizontal=True,
    key="style_radio",
)
team_style_key, style_desc = STYLE_DESCRIPTIONS[style_label]

st.markdown(
    f"<div style='background-color:#1a4d2e;border:1px solid #d4a017;border-radius:8px;"
    f"padding:12px 16px;color:#e8e8e8;margin-top:8px;'>"
    f"<strong style='color:#d4a017;'>{style_label}</strong> — {style_desc}"
    f"</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Competition / Match / Player
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("② Sélection Compétition / Match / Joueur")

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_competitions() -> pd.DataFrame:
    return list_competitions()

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_matches(comp_id: int, season_id: int) -> pd.DataFrame:
    return list_matches(comp_id, season_id)

@st.cache_data(ttl=1800, show_spinner=False)
def _cached_events(match_id: int) -> pd.DataFrame:
    return load_events(match_id)

with st.spinner("Chargement des compétitions..."):
    comps = _cached_competitions()

if comps.empty:
    st.error("Impossible de charger les compétitions StatsBomb.")
    st.stop()

comp_options = {
    f"{row['competition_name']} — {row['season_name']}": (row["competition_id"], row["season_id"])
    for _, row in comps.iterrows()
}

col_comp, col_match = st.columns(2)

with col_comp:
    comp_label = st.selectbox("Compétition / Saison", list(comp_options.keys()), key="comp_tac")
    comp_id, season_id = comp_options[comp_label]

with st.spinner("Chargement des matchs..."):
    matches = _cached_matches(comp_id, season_id)

if matches.empty:
    st.warning("Aucun match disponible pour cette compétition/saison.")
    st.stop()

match_labels = {get_match_label(row): row["match_id"] for _, row in matches.iterrows()}

with col_match:
    match_label = st.selectbox("Match", list(match_labels.keys()), key="match_tac")

match_id = match_labels[match_label]

with st.spinner("Chargement des événements..."):
    events = _cached_events(match_id)

if events.empty:
    st.warning("Impossible de charger les événements du match.")
    st.stop()

players = get_players_in_match(events)
if not players:
    st.warning("Aucun joueur trouvé.")
    st.stop()

# Detect player position
def _detect_position(events_df: pd.DataFrame, name: str) -> str:
    if "position" in events_df.columns:
        pos = events_df[events_df["player"] == name]["position"].dropna()
        if not pos.empty:
            return str(pos.iloc[0])
    return "Center Midfield"

col_player, col_pos = st.columns(2)

with col_player:
    player_name = st.selectbox("Joueur", players, key="player_tac")

detected_pos = _detect_position(events, player_name)

with col_pos:
    # Offer editable position field (pre-filled with detected)
    player_position = st.text_input(
        "Poste (StatsBomb)",
        value=detected_pos,
        key="pos_tac",
        help="Poste StatsBomb détecté automatiquement. Modifiable si nécessaire.",
    )

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Phase formation configuration
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("③ Configuration des Phases de Jeu")

st.markdown(
    "<p style='color:#a8c5b0;'>Définissez la formation utilisée dans chacune des 3 phases tactiques.</p>",
    unsafe_allow_html=True,
)

AVAILABLE_FORMATIONS = [
    "4-3-3", "3-4-3", "3-2-5", "4-4-2", "4-2-3-1",
    "5-3-2", "3-5-2", "4-1-4-1", "4-3-3 (attack)", "3-4-1-2",
]

col_ph1, col_ph2, col_ph3 = st.columns(3)

with col_ph1:
    st.markdown("**Phase de Construction**")
    st.caption("Sortie de balle depuis le bloc défensif")
    formation_buildup = st.selectbox(
        "Formation (construction)",
        AVAILABLE_FORMATIONS,
        index=AVAILABLE_FORMATIONS.index("4-3-3"),
        key="ph_buildup",
        label_visibility="collapsed",
    )

with col_ph2:
    st.markdown("**Phase de Progression**")
    st.caption("Avancée dans les 2/3 médians")
    formation_progression = st.selectbox(
        "Formation (progression)",
        AVAILABLE_FORMATIONS,
        index=AVAILABLE_FORMATIONS.index("3-4-3"),
        key="ph_prog",
        label_visibility="collapsed",
    )

with col_ph3:
    st.markdown("**Phase de Finition**")
    st.caption("Création et conclusion dans le dernier tiers")
    formation_finish = st.selectbox(
        "Formation (finition)",
        AVAILABLE_FORMATIONS,
        index=AVAILABLE_FORMATIONS.index("3-2-5"),
        key="ph_finish",
        label_visibility="collapsed",
    )

phase_config = {
    "buildup": formation_buildup,
    "progression": formation_progression,
    "finish": formation_finish,
}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Run analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
run_col, _ = st.columns([1, 3])
with run_col:
    run_analysis = st.button(
        "⚡ Lancer l'Analyse Tactique",
        key="run_tac",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if run_analysis:
    with st.spinner(f"Analyse tactique de {player_name} en cours…"):
        try:
            report: MatchReport = compute_tactical_score(
                events_df=events,
                player_name=player_name,
                player_position=player_position,
                team_style=team_style_key,
                phase_config=phase_config,
                match_id=match_id,
            )
        except Exception as exc:
            st.error(f"Erreur lors de l'analyse : {exc}")
            st.stop()

    st.markdown("---")
    st.subheader(f"📊 Résultats — {player_name}")

    # ── Big score badge ────────────────────────────────────────────────────
    score = report.tactical_compatibility_score
    if score >= 65:
        score_class = "score-green"
        score_emoji = "✅"
        score_label = "Excellente compatibilité"
    elif score >= 40:
        score_class = "score-orange"
        score_emoji = "⚠️"
        score_label = "Compatibilité modérée"
    else:
        score_class = "score-red"
        score_emoji = "❌"
        score_label = "Compatibilité faible"

    st.markdown(
        f"<div class='score-badge {score_class}'>"
        f"{score_emoji} Score de Compatibilité Tactique : {score:.0f} / 100"
        f"<br><span style='font-size:1rem;font-weight:400;'>{score_label} — {style_label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── KPI metrics ────────────────────────────────────────────────────────
    st.markdown("#### Indicateurs Clés de Performance")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.metric(
            label="🔥 Pressings / 90",
            value=f"{report.pressing_triggers}",
            help="Nombre d'actions de pressing par 90 minutes",
        )
    with kpi_col2:
        st.metric(
            label="➡️ Passes verticales",
            value=f"{report.vertical_passes_ratio * 100:.1f}%",
            help="Ratio de passes progressives / total passes",
        )
    with kpi_col3:
        st.metric(
            label="🎯 Polyvalence tactique",
            value=f"{report.versatility_score:.1f} / 10",
            help="Score de couverture des zones tactiques sur les 3 phases",
        )
    with kpi_col4:
        st.metric(
            label="⚡ Contre-pressing",
            value=f"{report.counterpressing_efficiency * 100:.1f}%",
            help="Efficacité du contre-pressing après perte de balle",
        )

    kpi_col5, kpi_col6, kpi_col7, kpi_col8 = st.columns(4)

    with kpi_col5:
        st.metric(
            label="📏 Distance estimée",
            value=f"{report.distance_estimate_km:.1f} km",
            help="Estimation proxy de la distance parcourue",
        )
    with kpi_col6:
        st.metric(
            label="🔀 Demi-espaces",
            value=f"{report.half_space_runs}",
            help="Actions dans les demi-espaces (zones dangereuses latérales)",
        )
    with kpi_col7:
        st.metric(
            label="🔄 Décrochages",
            value=f"{report.false_nine_drops}",
            help="Décrochages axiaux (joueur reçoit la balle dans le tiers médian)",
        )
    with kpi_col8:
        st.metric(
            label="🏟️ Possession équipe",
            value=f"{report.possession_share * 100:.1f}%",
            help="Part des événements générée par l'équipe du joueur",
        )

    # ── Radar chart ────────────────────────────────────────────────────────
    st.markdown("---")
    col_radar, col_feedback = st.columns([1, 1])

    with col_radar:
        st.markdown("#### 🕸️ Radar Tactique")

        # Build radar from tactical dimensions
        radar_labels = [
            "Pressing", "Contre-\npressing", "Distance", "Passes\nverticales",
            "Polyvalence", "Demi-\nespaces",
        ]

        def _norm_radar(val: float, lo: float, hi: float) -> float:
            if hi <= lo:
                return 0.0
            return max(0.0, min(1.0, (val - lo) / (hi - lo)))

        player_scores = [
            _norm_radar(report.pressing_triggers, 0, 30),
            report.counterpressing_efficiency,
            _norm_radar(report.distance_estimate_km, 4, 14),
            _norm_radar(report.vertical_passes_ratio, 0, 0.7),
            _norm_radar(report.versatility_score, 0, 10),
            _norm_radar(report.half_space_runs, 0, 20),
        ]

        N = len(radar_labels)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles_closed = angles + [angles[0]]
        vals_closed = player_scores + [player_scores[0]]

        PITCH_BG = "#0f1f14"
        GOLD = "#d4a017"
        GREEN = "#1a4d2e"
        TEXT_C = "#e8e8e8"

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor(PITCH_BG)
        ax.set_facecolor(PITCH_BG)

        ax.set_xticks(angles)
        ax.set_xticklabels(radar_labels, color=TEXT_C, fontsize=9)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(["20", "40", "60", "80", "100"], color="#666", fontsize=7)
        ax.spines["polar"].set_color(GOLD)
        ax.spines["polar"].set_alpha(0.4)
        for gl in ax.yaxis.get_gridlines():
            gl.set_color(GOLD)
            gl.set_alpha(0.15)

        # Score-based color
        if score >= 65:
            radar_color = "#2ecc71"
        elif score >= 40:
            radar_color = "#f39c12"
        else:
            radar_color = "#e74c3c"

        ax.fill(angles_closed, vals_closed, color=radar_color, alpha=0.25)
        ax.plot(angles_closed, vals_closed, color=radar_color, linewidth=2.5)
        ax.scatter(angles, player_scores, color=radar_color, s=60, zorder=5)

        # Annotate values
        raw_display = [
            f"{report.pressing_triggers}",
            f"{report.counterpressing_efficiency * 100:.0f}%",
            f"{report.distance_estimate_km:.1f}km",
            f"{report.vertical_passes_ratio * 100:.0f}%",
            f"{report.versatility_score:.1f}",
            f"{report.half_space_runs}",
        ]
        for angle, val_norm, label_val in zip(angles, player_scores, raw_display):
            ax.annotate(
                label_val,
                xy=(angle, val_norm),
                xytext=(0, 10),
                textcoords="offset points",
                color=GOLD,
                fontsize=8,
                ha="center",
            )

        ax.set_title(
            f"{player_name}\n{style_label}",
            color=GOLD,
            fontsize=11,
            pad=20,
        )

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_feedback:
        st.markdown("#### 💬 Observations Tactiques")

        if report.tactical_feedback:
            for observation in report.tactical_feedback:
                st.markdown(
                    f"<div class='feedback-item'>• {observation}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucune observation générée — données insuffisantes pour ce joueur.")

        # ── Phase mapping summary ──────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 🗺️ Cartographie par Phase")
        from engine.tactical_engine import PhaseMapper
        pm = PhaseMapper(phase_config)

        positions_in_match = []
        if "position" in events.columns:
            positions_in_match = (
                events[events["player"] == player_name]["position"]
                .dropna()
                .unique()
                .tolist()
            )
        if not positions_in_match:
            positions_in_match = [player_position]

        phase_data = []
        for pos in positions_in_match:
            phase_data.append({
                "Poste": pos,
                "Construction": pm.map_position(pos, "buildup"),
                "Progression": pm.map_position(pos, "progression"),
                "Finition": pm.map_position(pos, "finish"),
            })

        phase_df = pd.DataFrame(phase_data).drop_duplicates()
        st.dataframe(phase_df, use_container_width=True, hide_index=True)

    # ── JSON export ─────────────────────────────────────────────────────────
    st.markdown("---")
    export_col, _ = st.columns([1, 3])
    with export_col:
        json_bytes = report.to_json().encode("utf-8")
        st.download_button(
            label="⬇️ Télécharger le rapport (JSON)",
            data=json_bytes,
            file_name=f"rapport_tactique_{player_name.replace(' ', '_')}_{match_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    # ── Full data expander ─────────────────────────────────────────────────
    with st.expander("📋 Données brutes du rapport"):
        report_dict = report.to_dict()
        # Show feedback separately as list
        feedback_list = report_dict.pop("tactical_feedback", [])
        metrics_df = pd.DataFrame([
            {"Dimension": k.replace("_", " ").title(), "Valeur": str(v)}
            for k, v in report_dict.items()
        ])
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        if feedback_list:
            st.markdown("**Observations :**")
            for obs in feedback_list:
                st.markdown(f"- {obs}")

else:
    # Placeholder before analysis is run
    st.markdown(
        "<div style='text-align:center;padding:40px;color:#a8c5b0;'>"
        "<span style='font-size:3rem;'>🧭</span><br><br>"
        "Configurez les paramètres ci-dessus puis cliquez sur "
        "<strong style='color:#d4a017;'>⚡ Lancer l'Analyse Tactique</strong>"
        "</div>",
        unsafe_allow_html=True,
    )
