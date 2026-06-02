"use client";
import type { Match } from "@/lib/types";

interface Props { matches: Match[]; onSelect: (m: Match) => void; disabled?: boolean; }

export default function MatchSelect({ matches, onSelect, disabled }: Props) {
  return (
    <div>
      <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>
        Match
      </label>
      <select
        disabled={disabled || matches.length === 0}
        onChange={e => {
          const m = matches.find(x => String(x.match_id) === e.target.value);
          if (m) onSelect(m);
        }}
        style={{
          width: "100%", background: "#111a13", color: matches.length === 0 ? "#7a9e82" : "#e2ede5",
          border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px",
          padding: "9px 12px", fontSize: "0.82rem", cursor: "pointer", outline: "none",
        }}
      >
        <option value="">— Sélectionner —</option>
        {matches.map(m => <option key={m.match_id} value={m.match_id}>{m.label}</option>)}
      </select>
    </div>
  );
}
