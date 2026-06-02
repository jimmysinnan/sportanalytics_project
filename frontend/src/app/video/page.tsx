import TopBar from "@/components/layout/TopBar";

export default function VideoPage() {
  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="🎬 Analyse Vidéo" badge="Bientôt disponible" badgeVariant="cyan" />
      <div style={{
        border: "2px dashed rgba(0,229,255,0.35)", borderRadius: "14px",
        padding: "60px 20px", textAlign: "center",
        background: "rgba(0,229,255,0.03)", marginTop: "20px",
      }}>
        <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🎬</div>
        <h3 style={{ color: "#00e5ff", fontSize: "1.1rem", marginBottom: "8px" }}>Analyse Vidéo — En développement</h3>
        <p style={{ color: "#7a9e82", fontSize: "0.85rem", maxWidth: "480px", margin: "0 auto", lineHeight: 1.65 }}>
          Upload de clips vidéo + overlays automatiques (vitesse, trajectoire, zones de pression).
          Export enrichi avec métriques synchronisées.
        </p>
        <div style={{ marginTop: "20px", display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap" }}>
          {["🏃 Tracking vitesse", "📍 Heatmap dynamique", "🎯 Overlay xG", "📤 Export annoté"].map(f => (
            <span key={f} style={{
              fontSize: "0.72rem", padding: "5px 14px", borderRadius: "20px",
              border: "1px solid rgba(0,229,255,0.3)", color: "#00e5ff",
              background: "rgba(0,229,255,0.07)",
            }}>{f}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
