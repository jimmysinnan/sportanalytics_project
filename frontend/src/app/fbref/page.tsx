"use client";
import { useState, useEffect } from "react";
import TopBar from "@/components/layout/TopBar";
import { KpiGrid, CardSection } from "@/components/analytics";
import type { KpiItem } from "@/components/analytics";
import { api } from "@/lib/api";
import type { FBrefPlayer } from "@/lib/types";

export default function FBrefPage() {
  const [leagues, setLeagues] = useState<Record<string, string>>({});
  const [seasons, setSeasons] = useState<string[]>([]);
  const [selectedLeague, setSelectedLeague] = useState("");
  const [selectedSeason, setSelectedSeason] = useState("2024-2025");
  const [players, setPlayers] = useState<FBrefPlayer[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.fbrefLeagues().then(d => { setLeagues(d.leagues); setSeasons(d.seasons); }).catch(() => {});
  }, []);

  async function loadData(league: string, season: string) {
    if (!league) return;
    setLoading(true);
    try {
      const d = await api.fbrefPlayers(league, season);
      setPlayers(d.players);
    } catch(e) { console.error(e); setPlayers([]); }
    setLoading(false);
  }

  function onLeagueChange(val: string) { setSelectedLeague(val); loadData(val, selectedSeason); }
  function onSeasonChange(val: string) { setSelectedSeason(val); if (selectedLeague) loadData(selectedLeague, val); }

  const filtered = players.filter(p => !search || String(p.player ?? "").toLowerCase().includes(search.toLowerCase()) || String(p.team ?? "").toLowerCase().includes(search.toLowerCase()));

  const kpis: KpiItem[] = [
    { label: "Joueurs chargés", value: players.length, deltaUp: players.length > 0 },
    { label: "Ligue", value: Object.entries(leagues).find(([,v]) => v === selectedLeague)?.[0]?.split(" ")[0] ?? "—" },
    { label: "Saison", value: selectedSeason },
    { label: "Source", value: "FBref", delta: "Live data", deltaUp: true, deltaCyan: true },
  ];

  const selectStyle = {
    background: "#111a13", color: "#e2ede5",
    border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px",
    padding: "9px 12px", fontSize: "0.82rem", cursor: "pointer", outline: "none",
  };

  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="📡 Données Live" badge="FBref 2024-2025" badgeVariant="cyan" />
      <p style={{ color: "#7a9e82", marginBottom: "20px", fontSize: "0.85rem" }}>
        Stats joueurs saison en cours via FBref — <span style={{ color: "#39ff6a" }}>mise à jour hebdomadaire</span>. Complète les données historiques StatsBomb.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "20px" }}>
        <div>
          <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>Ligue</label>
          <select onChange={e => onLeagueChange(e.target.value)} value={selectedLeague} style={{ width: "100%", ...selectStyle }}>
            <option value="">— Sélectionner —</option>
            {Object.entries(leagues).map(([label, key]) => <option key={key} value={key}>{label}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>Saison</label>
          <select onChange={e => onSeasonChange(e.target.value)} value={selectedSeason} style={{ width: "100%", ...selectStyle }}>
            {seasons.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>Recherche</label>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Nom joueur ou équipe..."
            style={{ width: "100%", background: "#111a13", color: "#e2ede5", border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px", padding: "9px 12px", fontSize: "0.82rem", outline: "none" }} />
        </div>
      </div>

      {players.length > 0 && <KpiGrid kpis={kpis} cols={4} />}

      {loading && <div style={{ textAlign: "center", padding: "40px", color: "#7a9e82", fontSize: "0.85rem" }}>⚡ Chargement FBref...</div>}

      {!loading && filtered.length > 0 && (
        <CardSection title={`📊 Joueurs — ${filtered.length} résultats`}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem" }}>
              <thead>
                <tr>
                  {["Joueur","Équipe","Poste","Matchs","Buts","Passes déc.","xG"].map(h => (
                    <th key={h} style={{ color: "#00e5ff", textAlign: "left", padding: "8px 10px", borderBottom: "1px solid rgba(0,229,255,0.18)", fontSize: "0.68rem", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 50).map((p, i) => (
                  <tr key={i} style={{ cursor: "default" }}
                    onMouseEnter={e => (e.currentTarget.style.background = "rgba(57,255,106,0.03)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}>
                    <td style={{ padding: "7px 10px", color: "#e2ede5", borderBottom: "1px solid rgba(255,255,255,0.03)", fontWeight: 600 }}>{p.player ?? "—"}</td>
                    <td style={{ padding: "7px 10px", color: "#7a9e82", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{p.team ?? "—"}</td>
                    <td style={{ padding: "7px 10px", color: "#39ff6a", borderBottom: "1px solid rgba(255,255,255,0.03)", fontSize: "0.7rem" }}>{p.pos ?? "—"}</td>
                    <td style={{ padding: "7px 10px", color: "#7a9e82", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{p.games ?? "—"}</td>
                    <td style={{ padding: "7px 10px", color: "#e2ede5", borderBottom: "1px solid rgba(255,255,255,0.03)", fontWeight: 600 }}>{p.goals ?? 0}</td>
                    <td style={{ padding: "7px 10px", color: "#e2ede5", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{p.assists ?? 0}</td>
                    <td style={{ padding: "7px 10px", color: "#00e5ff", borderBottom: "1px solid rgba(255,255,255,0.03)" }}>{typeof p.xg === "number" ? p.xg.toFixed(2) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length > 50 && <p style={{ color: "#7a9e82", fontSize: "0.75rem", marginTop: "8px", textAlign: "center" }}>Affichage des 50 premiers résultats sur {filtered.length}</p>}
          </div>
        </CardSection>
      )}

      {!loading && !selectedLeague && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7a9e82" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>📡</div>
          <p style={{ fontSize: "0.88rem" }}>Sélectionnez une ligue pour charger les données FBref de la saison en cours.</p>
          <p style={{ fontSize: "0.78rem", marginTop: "8px", color: "#39ff6a" }}>Premier chargement ~10s (scraping FBref)</p>
        </div>
      )}
    </div>
  );
}
