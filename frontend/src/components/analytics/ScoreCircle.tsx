interface Props { score: number; label?: string; }

export default function ScoreCircle({ score, label = "/100" }: Props) {
  const color = score >= 65 ? "#39ff6a" : score >= 40 ? "#ffa040" : "#ff4444";
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "12px 0" }}>
      <div style={{
        width: "120px", height: "120px", borderRadius: "50%",
        background: "radial-gradient(circle, #0f2015 0%, #080c0a 100%)",
        boxShadow: `0 0 0 3px ${color}66, 0 0 30px ${color}26`,
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      }}>
        <div className="text-grad" style={{ fontSize: "2.4rem", fontWeight: 800, lineHeight: 1 }}>{score.toFixed(0)}</div>
        <div style={{ fontSize: "0.6rem", color: "#7a9e82" }}>{label}</div>
      </div>
    </div>
  );
}
