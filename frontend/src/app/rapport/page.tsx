"use client";
import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import { CompetitionSelect, MatchSelect, PlayerSelect } from "@/components/selectors";
import { CardSection } from "@/components/analytics";
import { api } from "@/lib/api";
import type { Competition, Match } from "@/lib/types";

export default function RapportPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [compLabel, setCompLabel] = useState("");
  const [observations, setObservations] = useState("");
  const [generating, setGenerating] = useState(false);
  const [done, setDone] = useState(false);

  async function onCompSelect(comp: Competition) {
    setCompLabel(`${comp.competition_name} — ${comp.season_name}`);
    const d = await api.matches(comp.competition_id, comp.season_id);
    setMatches(d.matches);
  }
  async function onMatchSelect(m: Match) {
    setSelectedMatch(m);
    const d = await api.players(m.match_id);
    setPlayers(d.players);
  }
  function onPlayerSelect(player: string) { setSelectedPlayer(player); setDone(false); }

  async function handleDownload() {
    if (!selectedMatch || !selectedPlayer) return;
    setGenerating(true); setDone(false);
    try {
      const blob = await api.downloadPdf({
        match_id: selectedMatch.match_id, player_name: selectedPlayer,
        position: "Milieu", competition_label: compLabel, observations,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `rapport_${selectedPlayer.replace(/ /g,"_")}_${selectedMatch.match_id}.pdf`;
      document.body.appendChild(a); a.click();
      document.body.removeChild(a); URL.revokeObjectURL(url);
      setDone(true);
    } catch(e) { console.error(e); }
    setGenerating(false);
  }

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="📄 Rapport PDF" badge="Export Professionnel" />

      <p style={{ color: "#7a9e82", marginBottom: "24px", fontSize: "0.88rem" }}>
        Générez un rapport tactique brandé <span className="text-grad" style={{ fontWeight: 700 }}>la soccer Machine</span> avec heatmap, radar et observations personnalisables.
      </p>

      <CardSection title="① Sélection Match & Joueur">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
          <CompetitionSelect onSelect={onCompSelect} />
          <MatchSelect matches={matches} onSelect={onMatchSelect} disabled={matches.length === 0} />
          <PlayerSelect players={players} onSelect={onPlayerSelect} disabled={players.length === 0} />
        </div>
      </CardSection>

      <div style={{ marginTop: "18px" }}>
        <CardSection title="② Observations Tactiques (optionnel)" cyan>
          <textarea
            value={observations}
            onChange={e => setObservations(e.target.value)}
            placeholder="Laissez vide pour une synthèse auto-générée, ou personnalisez votre analyse..."
            rows={5}
            style={{
              width: "100%", background: "#0d1510", color: "#e2ede5",
              border: "1px solid rgba(0,229,255,0.25)", borderRadius: "8px",
              padding: "12px", fontSize: "0.82rem", resize: "vertical", outline: "none",
              lineHeight: 1.6,
            }}
          />
        </CardSection>
      </div>

      <div style={{ marginTop: "18px" }}>
        <button
          onClick={handleDownload}
          disabled={!selectedPlayer || generating}
          style={{
            background: selectedPlayer && !generating ? "linear-gradient(135deg, #39ff6a, #00e5ff)" : "rgba(57,255,106,0.2)",
            color: selectedPlayer && !generating ? "#080c0a" : "#7a9e82",
            border: "none", borderRadius: "8px", padding: "14px 36px",
            fontWeight: 800, fontSize: "0.95rem",
            cursor: selectedPlayer && !generating ? "pointer" : "not-allowed",
            letterSpacing: "0.04em",
          }}
        >
          {generating ? "⏳ Génération en cours..." : "🖨️ Générer & Télécharger le PDF"}
        </button>

        {done && (
          <div style={{
            marginTop: "12px", display: "inline-flex", alignItems: "center", gap: "8px",
            background: "rgba(57,255,106,0.08)", border: "1px solid rgba(57,255,106,0.3)",
            borderRadius: "8px", padding: "8px 16px", fontSize: "0.82rem", color: "#39ff6a",
          }}>
            ✅ Rapport généré avec succès — téléchargement lancé
          </div>
        )}
      </div>
    </div>
  );
}
