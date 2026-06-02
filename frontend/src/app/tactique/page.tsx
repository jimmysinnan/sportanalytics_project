"use client";
import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import { CompetitionSelect, MatchSelect, PlayerSelect } from "@/components/selectors";
import { KpiGrid, FeedbackList, CardSection, ScoreCircle, BarRow } from "@/components/analytics";
import type { KpiItem } from "@/components/analytics";
import { api } from "@/lib/api";
import type { Competition, Match, TacticalReport } from "@/lib/types";

const STYLES = [
  { key: "positional", label: "Jeu Positionnel", desc: "Possession, rotations, jeu entre les lignes" },
  { key: "high-press", label: "Pressing Haut", desc: "Récupération haute, contre-pressing, intensité" },
  { key: "counter", label: "Contre-Attaque", desc: "Transitions rapides, verticalité, profondeur" },
  { key: "hybrid", label: "Hybride", desc: "Système flexible, pondération équilibrée" },
];
const FORMATIONS = ["4-3-3","3-4-3","3-2-5","4-4-2","4-2-3-1","5-3-2","3-5-2"];

export default function TactiquePage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [playerPos, setPlayerPos] = useState("Center Midfield");
  const [style, setStyle] = useState("positional");
  const [phases, setPhases] = useState({ buildup: "4-3-3", progression: "3-4-3", finish: "3-2-5" });
  const [report, setReport] = useState<TacticalReport | null>(null);
  const [loading, setLoading] = useState(false);

  async function onCompSelect(comp: Competition) {
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches); setReport(null);
  }
  async function onMatchSelect(m: Match) {
    setSelectedMatch(m);
    const d = await api.players(m.match_id);
    setPlayers(d.players); setReport(null);
  }
  function onPlayerSelect(player: string) { setSelectedPlayer(player); setReport(null); }

  async function runAnalysis() {
    if (!selectedMatch || !selectedPlayer) return;
    setLoading(true);
    try {
      const r = await api.tacticalScore({
        match_id: selectedMatch.match_id, player_name: selectedPlayer,
        player_position: playerPos, team_style: style, phase_config: phases,
      });
      setReport(r);
    } catch(e) { console.error(e); }
    setLoading(false);
  }

  const kpis: KpiItem[] = report ? [
    { label: "Pressings /90", value: report.pressing_triggers },
    { label: "Passes verticales", value: `${(report.vertical_passes_ratio * 100).toFixed(1)}%`, deltaUp: report.vertical_passes_ratio >= 0.3 },
    { label: "Contre-pressing", value: `${(report.counterpressing_efficiency * 100).toFixed(1)}%`, deltaUp: report.counterpressing_efficiency >= 0.4 },
    { label: "Polyvalence", value: `${report.versatility_score.toFixed(1)}/10`, deltaUp: report.versatility_score >= 6 },
    { label: "Distance est.", value: `${report.distance_estimate_km.toFixed(1)} km`, deltaUp: report.distance_estimate_km >= 9 },
    { label: "Demi-espaces", value: report.half_space_runs },
    { label: "Décrochages", value: report.false_nine_drops },
    { label: "Possession éq.", value: `${(report.possession_share * 100).toFixed(1)}%` },
  ] : [];

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="🧠 Score Tactique" badge="0–100" badgeVariant="cyan" />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} disabled={matches.length === 0} />
        <PlayerSelect players={players} onSelect={onPlayerSelect} disabled={players.length === 0} />
      </div>

      {/* Style selector */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "10px", marginBottom: "20px" }}>
        {STYLES.map(s => (
          <button key={s.key} onClick={() => setStyle(s.key)} style={{
            background: style === s.key ? "rgba(57,255,106,0.1)" : "#111a13",
            border: `1px solid ${style === s.key ? "#39ff6a" : "rgba(57,255,106,0.18)"}`,
            borderRadius: "10px", padding: "12px", cursor: "pointer", textAlign: "left",
          }}>
            <div style={{ fontSize: "0.78rem", fontWeight: 700, color: style === s.key ? "#39ff6a" : "#e2ede5", marginBottom: "4px" }}>{s.label}</div>
            <div style={{ fontSize: "0.68rem", color: "#7a9e82", lineHeight: 1.4 }}>{s.desc}</div>
          </button>
        ))}
      </div>

      {/* Phases + position */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "12px", marginBottom: "20px" }}>
        {(["buildup","progression","finish"] as const).map(ph => (
          <div key={ph}>
            <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>
              {ph === "buildup" ? "Construction" : ph === "progression" ? "Progression" : "Finition"}
            </label>
            <select value={phases[ph]} onChange={e => setPhases(p => ({...p, [ph]: e.target.value}))}
              style={{ width: "100%", background: "#111a13", color: "#e2ede5", border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px", padding: "8px 10px", fontSize: "0.8rem", outline: "none" }}>
              {FORMATIONS.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
        ))}
        <div>
          <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>Poste</label>
          <input value={playerPos} onChange={e => setPlayerPos(e.target.value)}
            style={{ width: "100%", background: "#111a13", color: "#e2ede5", border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px", padding: "8px 10px", fontSize: "0.8rem", outline: "none" }} />
        </div>
      </div>

      <button onClick={runAnalysis} disabled={!selectedPlayer || loading} style={{
        background: selectedPlayer && !loading ? "linear-gradient(135deg, #39ff6a, #00e5ff)" : "rgba(57,255,106,0.2)",
        color: selectedPlayer && !loading ? "#080c0a" : "#7a9e82",
        border: "none", borderRadius: "8px", padding: "12px 28px",
        fontWeight: 800, fontSize: "0.9rem", cursor: selectedPlayer ? "pointer" : "not-allowed",
        marginBottom: "24px",
      }}>⚡ {loading ? "Analyse en cours..." : "Lancer l'Analyse Tactique"}</button>

      {report && !loading && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "18px", alignItems: "center", marginBottom: "18px" }}>
            <div style={{ background: "#111a13", border: "1px solid rgba(57,255,106,0.18)", borderRadius: "12px", padding: "20px" }}>
              <ScoreCircle score={report.tactical_compatibility_score} />
              <div style={{ textAlign: "center", fontSize: "0.75rem", color: "#7a9e82", marginTop: "8px" }}>
                {STYLES.find(s => s.key === style)?.label}
              </div>
            </div>
            <CardSection title="💬 Observations Tactiques">
              <FeedbackList items={report.tactical_feedback.map(t => ({ text: t, ok: !t.includes("insuffisant") && !t.includes("faible") && !t.includes("trop") }))} />
            </CardSection>
          </div>
          <KpiGrid kpis={kpis} cols={4} />
          <CardSection title="📊 Dimensions Tactiques" cyan>
            <BarRow label="Pressing" value={String(report.pressing_triggers)} pct={Math.min(report.pressing_triggers * 3, 100)} />
            <BarRow label="Contre-pressing" value={`${(report.counterpressing_efficiency*100).toFixed(0)}%`} pct={report.counterpressing_efficiency * 100} />
            <BarRow label="Passes verticales" value={`${(report.vertical_passes_ratio*100).toFixed(0)}%`} pct={report.vertical_passes_ratio * 100 / 0.7} cyan />
            <BarRow label="Polyvalence" value={`${report.versatility_score.toFixed(1)}/10`} pct={report.versatility_score * 10} cyan />
            <BarRow label="Distance" value={`${report.distance_estimate_km.toFixed(1)} km`} pct={((report.distance_estimate_km - 4) / 10) * 100} />
          </CardSection>
        </>
      )}

      {!loading && !report && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7a9e82" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🧠</div>
          <p style={{ fontSize: "0.88rem" }}>Configurez les paramètres puis lancez l&apos;analyse tactique.</p>
        </div>
      )}
    </div>
  );
}
