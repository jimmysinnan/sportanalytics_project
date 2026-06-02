"use client";
import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import { CompetitionSelect, MatchSelect, PlayerSelect } from "@/components/selectors";
import { KpiGrid, PitchImage, CardSection } from "@/components/analytics";
import type { KpiItem } from "@/components/analytics";
import { api } from "@/lib/api";
import type { Competition, Match } from "@/lib/types";

const ACTION_OPTS = [
  { value: "all", label: "Toutes actions" },
  { value: "Pass", label: "Passes" },
  { value: "Carry", label: "Conduites" },
  { value: "Pressure", label: "Pressings" },
  { value: "Shot", label: "Tirs" },
  { value: "Dribble", label: "Dribbles" },
];

export default function HeatmapPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [action, setAction] = useState("all");
  const [hmFull, setHmFull] = useState("");
  const [hm1, setHm1] = useState("");
  const [hm2, setHm2] = useState("");
  const [loading, setLoading] = useState(false);

  async function onCompSelect(comp: Competition) {
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches);
    setPlayers([]); setSelectedPlayer(""); setHmFull(""); setHm1(""); setHm2("");
  }

  async function onMatchSelect(m: Match) {
    setSelectedMatch(m);
    const d = await api.players(m.match_id);
    setPlayers(d.players);
    setSelectedPlayer(""); setHmFull(""); setHm1(""); setHm2("");
  }

  async function loadHeatmaps(player: string, act: string) {
    if (!selectedMatch) return;
    setLoading(true);
    try {
      const [full, h1, h2] = await Promise.all([
        api.heatmap(selectedMatch.match_id, player, act, "full"),
        api.heatmap(selectedMatch.match_id, player, act, "1"),
        api.heatmap(selectedMatch.match_id, player, act, "2"),
      ]);
      setHmFull(full.image_b64); setHm1(h1.image_b64); setHm2(h2.image_b64);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  async function onPlayerSelect(player: string) {
    setSelectedPlayer(player);
    await loadHeatmaps(player, action);
  }

  async function onActionChange(act: string) {
    setAction(act);
    if (selectedPlayer) await loadHeatmaps(selectedPlayer, act);
  }

  const kpis: KpiItem[] = [
    { label: "Joueur", value: selectedPlayer || "—" },
    { label: "Filtre", value: ACTION_OPTS.find(o => o.value === action)?.label ?? action },
    { label: "Match", value: selectedMatch ? `${selectedMatch.home_team} vs ${selectedMatch.away_team}` : "—" },
  ];

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="Heatmap &amp; Zones" badge={selectedPlayer || "StatsBomb Open Data"} />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <CompetitionSelect onSelect={onCompSelect} />
        <MatchSelect matches={matches} onSelect={onMatchSelect} disabled={matches.length === 0} />
        <PlayerSelect players={players} onSelect={onPlayerSelect} disabled={players.length === 0} />
      </div>

      {selectedPlayer && (
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "20px" }}>
          {ACTION_OPTS.map(o => (
            <button key={o.value} onClick={() => onActionChange(o.value)} style={{
              padding: "6px 14px", borderRadius: "20px", fontSize: "0.76rem", cursor: "pointer",
              border: `1px solid ${action === o.value ? "#39ff6a" : "rgba(57,255,106,0.25)"}`,
              background: action === o.value ? "rgba(57,255,106,0.15)" : "transparent",
              color: action === o.value ? "#39ff6a" : "#7a9e82",
            }}>{o.label}</button>
          ))}
        </div>
      )}

      {loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#7a9e82", fontSize: "0.85rem" }}>
          Génération des heatmaps...
        </div>
      )}

      {hmFull && !loading && (
        <>
          <KpiGrid kpis={kpis} cols={3} />
          <CardSection title="Heatmap — Match Complet">
            <PitchImage b64={hmFull} alt={`Heatmap ${selectedPlayer}`} />
          </CardSection>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px", marginTop: "18px" }}>
            <CardSection title="1ère Mi-Temps">
              <PitchImage b64={hm1} alt="1ère mi-temps" />
            </CardSection>
            <CardSection title="2ème Mi-Temps">
              <PitchImage b64={hm2} alt="2ème mi-temps" />
            </CardSection>
          </div>
        </>
      )}

      {!loading && !hmFull && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7a9e82" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🔥</div>
          <p style={{ fontSize: "0.88rem" }}>Sélectionnez un joueur pour visualiser ses zones d&apos;activité.</p>
        </div>
      )}
    </div>
  );
}
