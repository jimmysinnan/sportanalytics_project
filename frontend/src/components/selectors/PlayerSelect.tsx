"use client";
interface Props { players: string[]; onSelect: (p: string) => void; disabled?: boolean; }

export default function PlayerSelect({ players, onSelect, disabled }: Props) {
  return (
    <div>
      <label style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", display: "block", marginBottom: "6px" }}>
        Joueur
      </label>
      <select
        disabled={disabled || players.length === 0}
        onChange={e => onSelect(e.target.value)}
        style={{
          width: "100%", background: "#111a13", color: players.length === 0 ? "#7a9e82" : "#e2ede5",
          border: "1px solid rgba(57,255,106,0.25)", borderRadius: "8px",
          padding: "9px 12px", fontSize: "0.82rem", cursor: "pointer", outline: "none",
        }}
      >
        <option value="">— Sélectionner —</option>
        {players.map(p => <option key={p} value={p}>{p}</option>)}
      </select>
    </div>
  );
}
