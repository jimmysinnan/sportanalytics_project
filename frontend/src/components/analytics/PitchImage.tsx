interface Props { b64: string; alt?: string; }

export default function PitchImage({ b64, alt = "Visualisation tactique" }: Props) {
  if (!b64) {
    return (
      <div style={{
        width: "100%", paddingBottom: "65%", position: "relative",
        background: "#0f2818", borderRadius: "8px",
        border: "1px solid rgba(57,255,106,0.15)",
      }}>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: "32px", height: "32px", border: "3px solid rgba(57,255,106,0.3)", borderTopColor: "#39ff6a", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
        </div>
      </div>
    );
  }
  return (
    <img
      src={`data:image/png;base64,${b64}`}
      alt={alt}
      style={{ width: "100%", borderRadius: "8px", border: "1px solid rgba(57,255,106,0.15)", display: "block" }}
    />
  );
}
