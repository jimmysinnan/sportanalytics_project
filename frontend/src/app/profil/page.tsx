"use client";
import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import { CompetitionSelect, MatchSelect, PlayerSelect } from "@/components/selectors";
import { KpiGrid, BarRow, PitchImage, FeedbackList, CardSection } from "@/components/analytics";
import type { KpiItem } from "@/components/analytics";
import { api } from "@/lib/api";
import type { Competition, Match, PlayerMetrics } from "@/lib/types";

export default function ProfilPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [metrics, setMetrics] = useState<PlayerMetrics | null>(null);
  const [position, setPosition] = useState("");
  const [summary, setSummary] = useState("");
  const [radarB64, setRadarB64] = useState("");
  const [loading, setLoading] = useState(false);
  const [compLabel, setCompLabel] = useState("");

  async function onCompSelect(comp: Competition) {
    setCompLabel(`${comp.competition_name} — ${comp.season_name}`);
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches);
    setPlayers([]); setMetrics(null); setRadarB64(""); setSelectedPlayer("");
  }

  async function onMatchSelect(m: Match) {
    setSelectedMatch(m);
    const d = await api.players(m.match_id);
    setPlayers(d.players);
    setMetrics(null); setRadarB64(""); setSelectedPlayer("");
  }

  async function onPlayerSelect(player: string) {
    if (!selectedMatch) return;
    setSelectedPlayer(player);
    setLoading(true);
    try {
      const [statsD, radarD] = await Promise.all([
        api.playerStats(selectedMatch.match_id, player),
        api.radar(selectedMatch.match_id, player),
      ]);
      setMetrics(statsD.metrics);
      setPosition(statsD.position);
      setSummary(statsD.summary);
      setRadarB64(radarD.image_b64);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  const kpis: KpiItem[] = metrics ? [
    { label: "Minutes", value: metrics.minutes },
    { label: "Buts", value: metrics.goals, delta: metrics.xg > 0 ? `xG: ${metrics.xg.toFixed(2)}` : undefined, deltaUp: metrics.goals >= metrics.xg },
    { label: "Passes déc.", value: metrics.assists },
    { label: "Passes", value: metrics.passes, delta: `${metrics.pass_completion?.toFixed(1)}% réussies`, deltaUp: metrics.pass_completion >= 80 },
    { label: "Pressings", value: metrics.pressures, delta: `intensité ${(metrics.pressing_intensity * 100).toFixed(0)}%`, deltaUp: metrics.pressing_intensity >= 0.3 },
  ] : [];

  const feedbackItems = summary
    ? summary.split("\n\n")
        .filter(l => l.trim() && !l.startsWith("**Résumé") && !l.startsWith("*Poste"))
        .map(l => ({ text: l.replace(/^[⚡🔄⬇️🚀➡️💪⚔️🛡️🎯⚽]\s*/u, "").trim(), ok: !l.startsWith("⬇️") }))
        .filter(item => item.text.length > 0)
    : [];

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="Profil Joueur" badge={compLabel || "StatsBomb Open Data"} />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "24px" }}>
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} disabled={matches.length === 0} />
        <PlayerSelect players={players} onSelect={onPlayerSelect} disabled={players.length === 0} />
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#7a9e82", fontSize: "0.85rem" }}>
          Chargement des données...
        </div>
      )}

      {metrics && selectedPlayer && !loading && (
        <>
          {/* Player header */}
          <div style={{
            background: "#111a13", border: "1px solid rgba(57,255,106,0.18)",
            borderRadius: "12px", padding: "18px 22px", marginBottom: "18px",
            display: "flex", alignItems: "center", gap: "18px",
          }}>
            <div style={{
              width: "58px", height: "58px", borderRadius: "50%",
              background: "linear-gradient(135deg, #1a3020, #0d1510)",
              boxShadow: "0 0 0 2px rgba(57,255,106,0.3)",
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.6rem", flexShrink: 0,
            }}>⚽</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "1.15rem", fontWeight: 700, color: "#e2ede5" }}>{selectedPlayer}</div>
              <div style={{ fontSize: "0.78rem", color: "#7a9e82", marginTop: "2px" }}>{position}</div>
              <div style={{ display: "flex", gap: "6px", marginTop: "8px", flexWrap: "wrap" }}>
                {[position.split(" ").slice(-1)[0], `${metrics.minutes} min`,
                  selectedMatch ? `${selectedMatch.home_team} vs ${selectedMatch.away_team}` : ""]
                  .filter(Boolean).map(tag => (
                  <span key={tag} style={{
                    fontSize: "0.65rem", background: "rgba(57,255,106,0.08)",
                    color: "#39ff6a", padding: "3px 10px", borderRadius: "20px",
                    border: "1px solid rgba(57,255,106,0.2)",
                  }}>{tag}</span>
                ))}
              </div>
            </div>
            <div style={{ textAlign: "right", flexShrink: 0 }}>
              <div style={{ fontSize: "0.7rem", color: "#7a9e82" }}>xG</div>
              <div className="text-grad" style={{ fontSize: "2rem", fontWeight: 800, lineHeight: 1.1 }}>
                {metrics.xg.toFixed(2)}
              </div>
              <div style={{ fontSize: "0.68rem", color: "#39ff6a", marginTop: "2px" }}>
                {metrics.goals > 0 ? `${metrics.goals} but(s)` : "Aucun but"}
              </div>
            </div>
          </div>

          <KpiGrid kpis={kpis} cols={5} />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px", marginBottom: "18px" }}>
            <CardSection title="Radar Tactique">
              <PitchImage b64={radarB64} alt="Radar tactique" />
            </CardSection>
            <CardSection title="KPIs Détaillés">
              <BarRow label="Tirs cadrés" value={`${metrics.shots_on_target}/${metrics.shots}`}
                pct={metrics.shots > 0 ? (metrics.shots_on_target / metrics.shots) * 100 : 0} />
              <BarRow label="Dribbles réussis" value={`${metrics.dribbles_completed}/${metrics.dribbles_attempted}`}
                pct={metrics.dribbles_attempted > 0 ? (metrics.dribbles_completed / metrics.dribbles_attempted) * 100 : 0} />
              <BarRow label="Duels gagnés" value={`${metrics.duels_won}/${metrics.duels}`}
                pct={metrics.duels > 0 ? (metrics.duels_won / metrics.duels) * 100 : 0} />
              <BarRow label="Pressing intensité" value={`${(metrics.pressing_intensity * 100).toFixed(0)}%`}
                pct={metrics.pressing_intensity * 100} />
              <BarRow label="Passes progressives" value={String(metrics.progressive_passes)}
                pct={Math.min(metrics.progressive_passes * 5, 100)} />
              <BarRow label="Actions défensives" value={String(metrics.defensive_actions)}
                pct={Math.min(metrics.defensive_actions * 4, 100)} cyan />
              <BarRow label="Passes clés" value={String(metrics.key_passes)}
                pct={Math.min(metrics.key_passes * 10, 100)} cyan />
              <BarRow label="Conduites de balle" value={String(metrics.carries)}
                pct={Math.min(metrics.carries * 2, 100)} />
            </CardSection>
          </div>

          <CardSection title="Observations Tactiques">
            {feedbackItems.length > 0
              ? <FeedbackList items={feedbackItems} />
              : <div style={{ color: "#7a9e82", fontSize: "0.82rem", whiteSpace: "pre-line" }}>{summary}</div>}
          </CardSection>
        </>
      )}

      {!loading && !metrics && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7a9e82" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>👤</div>
          <p style={{ fontSize: "0.88rem" }}>Sélectionnez une compétition, un match et un joueur pour commencer l&apos;analyse.</p>
        </div>
      )}
    </div>
  );
}
