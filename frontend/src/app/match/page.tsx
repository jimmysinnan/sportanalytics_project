"use client";
import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import { CompetitionSelect, MatchSelect } from "@/components/selectors";
import { KpiGrid, PitchImage, CardSection, BarRow } from "@/components/analytics";
import type { KpiItem } from "@/components/analytics";
import { api } from "@/lib/api";
import type { Competition, Match, MatchSummary } from "@/lib/types";

export default function MatchPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [summary, setSummary] = useState<MatchSummary | null>(null);
  const [activeTab, setActiveTab] = useState<"shots"|"xg"|"passes"|"lineups">("shots");
  const [imgH, setImgH] = useState(""); const [imgA, setImgA] = useState("");
  const [imgXg, setImgXg] = useState(""); const [imgNet, setImgNet] = useState("");
  const [lineups, setLineups] = useState<Record<string, object[]>>({});
  const [loading, setLoading] = useState(false);
  const [netTeam, setNetTeam] = useState("");

  async function onCompSelect(comp: Competition) {
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches); setSummary(null); setSelectedMatch(null);
  }

  async function onMatchSelect(m: Match) {
    setSelectedMatch(m); setLoading(true);
    try {
      const [sum, lu] = await Promise.all([api.matchSummary(m.match_id), api.lineups(m.match_id)]);
      setSummary(sum); setLineups(lu); setNetTeam(sum.home_team);
      const [sh, sa, xg] = await Promise.all([
        api.shotMap(m.match_id, sum.home_team),
        api.shotMap(m.match_id, sum.away_team),
        api.xgTimeline(m.match_id),
      ]);
      setImgH(sh.image_b64); setImgA(sa.image_b64); setImgXg(xg.image_b64);
    } catch(e) { console.error(e); }
    setLoading(false);
  }

  async function loadPassNetwork(team: string) {
    if (!selectedMatch) return;
    setNetTeam(team); setLoading(true);
    try { const d = await api.passNetwork(selectedMatch.match_id, team); setImgNet(d.image_b64); }
    catch(e) { console.error(e); }
    setLoading(false);
  }

  const kpis: KpiItem[] = summary ? [
    { label: `${summary.home_team.slice(0,12)} Possession`, value: `${summary.home_possession}%`, deltaUp: summary.home_possession > 50 },
    { label: `${summary.away_team.slice(0,12)} Possession`, value: `${summary.away_possession}%` },
    { label: "xG Domicile", value: summary.home_xg.toFixed(2), deltaUp: summary.home_xg > summary.away_xg },
    { label: "xG Extérieur", value: summary.away_xg.toFixed(2) },
    { label: "Tirs Dom.", value: summary.home_shots }, { label: "Tirs Ext.", value: summary.away_shots },
  ] : [];

  const TABS: { key: typeof activeTab; label: string }[] = [
    { key: "shots", label: "⚽ Shot Map" }, { key: "xg", label: "📈 xG Timeline" },
    { key: "passes", label: "🕸️ Réseau Passes" }, { key: "lineups", label: "📋 Compositions" },
  ];

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="📊 Analyse Match" badge={selectedMatch ? `${selectedMatch.home_team} vs ${selectedMatch.away_team}` : "StatsBomb"} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} disabled={matches.length === 0} />
      </div>

      {loading && <div style={{ textAlign: "center", padding: "20px", color: "#7a9e82", fontSize: "0.85rem" }}>⚡ Chargement...</div>}

      {summary && !loading && (
        <>
          {/* Score header */}
          <div style={{
            background: "#111a13", border: "1px solid rgba(57,255,106,0.18)", borderRadius: "12px",
            padding: "20px", textAlign: "center", marginBottom: "18px",
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "16px" }}>
              <span style={{ fontSize: "1.3rem", fontWeight: 700, color: "#e2ede5" }}>{summary.home_team}</span>
              <span className="text-grad" style={{ fontSize: "2.2rem", fontWeight: 900 }}>
                {selectedMatch?.home_score} — {selectedMatch?.away_score}
              </span>
              <span style={{ fontSize: "1.3rem", fontWeight: 700, color: "#e2ede5" }}>{summary.away_team}</span>
            </div>
          </div>

          <KpiGrid kpis={kpis} cols={6} />

          {/* Possession bar */}
          <div style={{ marginBottom: "20px" }}>
            <BarRow label={`Possession — ${summary.home_team} vs ${summary.away_team}`}
              value={`${summary.home_possession}% / ${summary.away_possession}%`}
              pct={summary.home_possession} />
          </div>

          {/* Tabs */}
          <div style={{ display: "flex", gap: "2px", marginBottom: "18px", borderBottom: "1px solid rgba(57,255,106,0.18)" }}>
            {TABS.map(t => (
              <button key={t.key} onClick={() => { setActiveTab(t.key); if (t.key === "passes" && !imgNet) loadPassNetwork(summary.home_team); }}
                style={{
                  padding: "8px 16px", cursor: "pointer", fontSize: "0.8rem",
                  color: activeTab === t.key ? "#00e5ff" : "#7a9e82",
                  borderBottom: activeTab === t.key ? "2px solid #00e5ff" : "2px solid transparent",
                  background: "transparent", border: "none", borderBottomStyle: "solid",
                  borderBottomWidth: "2px", borderBottomColor: activeTab === t.key ? "#00e5ff" : "transparent",
                  marginBottom: "-1px",
                }}
              >{t.label}</button>
            ))}
          </div>

          {activeTab === "shots" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px" }}>
              <CardSection title={`⚽ ${summary.home_team}`}><PitchImage b64={imgH} /></CardSection>
              <CardSection title={`⚽ ${summary.away_team}`}><PitchImage b64={imgA} /></CardSection>
            </div>
          )}
          {activeTab === "xg" && <CardSection title="📈 xG Cumulatif"><PitchImage b64={imgXg} /></CardSection>}
          {activeTab === "passes" && (
            <CardSection title="🕸️ Réseau de Passes">
              <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
                {[summary.home_team, summary.away_team].map(t => (
                  <button key={t} onClick={() => loadPassNetwork(t)} style={{
                    padding: "6px 14px", borderRadius: "20px", fontSize: "0.76rem", cursor: "pointer",
                    border: `1px solid ${netTeam === t ? "#39ff6a" : "rgba(57,255,106,0.25)"}`,
                    background: netTeam === t ? "rgba(57,255,106,0.15)" : "transparent",
                    color: netTeam === t ? "#39ff6a" : "#7a9e82",
                  }}>{t}</button>
                ))}
              </div>
              <PitchImage b64={imgNet} />
            </CardSection>
          )}
          {activeTab === "lineups" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px" }}>
              {Object.entries(lineups).slice(0, 2).map(([team, players]) => (
                <CardSection key={team} title={`📋 ${team}`}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem" }}>
                    <thead><tr>
                      <th style={{ color: "#00e5ff", textAlign: "left", padding: "6px 8px", borderBottom: "1px solid rgba(0,229,255,0.18)", fontSize: "0.68rem", textTransform: "uppercase" }}>#</th>
                      <th style={{ color: "#00e5ff", textAlign: "left", padding: "6px 8px", borderBottom: "1px solid rgba(0,229,255,0.18)", fontSize: "0.68rem", textTransform: "uppercase" }}>Joueur</th>
                    </tr></thead>
                    <tbody>
                      {(players as {jersey_number?: number; player_name?: string}[]).map((p, i) => (
                        <tr key={i}><td style={{ padding: "6px 8px", color: "#39ff6a", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{p.jersey_number ?? i+1}</td>
                        <td style={{ padding: "6px 8px", color: "#7a9e82", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{p.player_name ?? "—"}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </CardSection>
              ))}
            </div>
          )}
        </>
      )}
      {!loading && !summary && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7a9e82" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>📊</div>
          <p style={{ fontSize: "0.88rem" }}>Sélectionnez un match pour lancer l&apos;analyse complète.</p>
        </div>
      )}
    </div>
  );
}
