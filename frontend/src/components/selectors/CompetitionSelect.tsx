"use client";
import { useEffect, useState } from "react";
import type { Competition } from "@/lib/types";
import { api } from "@/lib/api";

interface Props { onSelect: (comp: Competition) => void; }

export default function CompetitionSelect({ onSelect }: Props) {
  const [comps, setComps] = useState<Competition[]>([]);
  useEffect(() => { api.competitions().then(d => setComps(d.competitions)).catch(() => {}); }, []);

  return (
    <div>
      <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>
        Compétition / Saison
      </label>
      <select
        onChange={e => {
          const [cId, sId] = e.target.value.split("|").map(Number);
          const comp = comps.find(c => c.competition_id === cId && c.season_id === sId);
          if (comp) onSelect(comp);
        }}
        style={{
          width: "100%", background: "#111a13", color: "#e2ede5",
          border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px",
          padding: "9px 12px", fontSize: "0.82rem", cursor: "pointer",
          outline: "none",
        }}
      >
        <option value="">— Sélectionner —</option>
        {comps.map(c => (
          <option key={`${c.competition_id}|${c.season_id}`} value={`${c.competition_id}|${c.season_id}`}>
            {c.competition_name} — {c.season_name}
          </option>
        ))}
      </select>
    </div>
  );
}
