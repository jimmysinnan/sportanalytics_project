interface Props {
  label: string;
  value: string | number;
  delta?: string;
  deltaUp?: boolean;
  deltaCyan?: boolean;
}

export default function KpiCard({ label, value, delta, deltaUp, deltaCyan }: Props) {
  return (
    <div style={{
      background: "#111a13", border: "1px solid rgba(57,255,106,0.18)",
      borderRadius: "10px", padding: "14px 18px", position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(57,255,106,0.04), transparent)", pointerEvents: "none" }} />
      <div style={{ fontSize: "0.68rem", color: "#7a9e82", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: "5px" }}>{label}</div>
      <div style={{ fontSize: "1.7rem", fontWeight: 700, color: "#e2ede5", lineHeight: 1 }}>{value}</div>
      {delta && (
        <div style={{ fontSize: "0.72rem", marginTop: "4px", color: deltaCyan ? "#00e5ff" : deltaUp ? "#39ff6a" : "#7a9e82" }}>
          {delta}
        </div>
      )}
    </div>
  );
}
