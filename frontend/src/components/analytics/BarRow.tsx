interface Props { label: string; value: string; pct: number; cyan?: boolean; }

export default function BarRow({ label, value, pct, cyan }: Props) {
  const fillColor = cyan
    ? "linear-gradient(90deg, rgba(0,229,255,0.6), #39ff6a)"
    : "linear-gradient(90deg, rgba(57,255,106,0.6), #00e5ff)";
  return (
    <div style={{ marginBottom: "10px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.76rem", color: "#7a9e82", marginBottom: "4px" }}>
        <span>{label}</span>
        <span style={{ color: cyan ? "#00e5ff" : "#39ff6a", fontWeight: 600 }}>{value}</span>
      </div>
      <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: "4px", height: "6px", overflow: "hidden" }}>
        <div style={{ height: "100%", borderRadius: "4px", background: fillColor, width: `${Math.min(Math.max(pct, 0), 100)}%` }} />
      </div>
    </div>
  );
}
