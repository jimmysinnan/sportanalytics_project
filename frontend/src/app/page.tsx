import TopBar from "@/components/layout/TopBar";
import Link from "next/link";

const FEATURES = [
  { href: "/profil",   icon: "👤", title: "Profil Joueur",    desc: "Radar tactique, KPIs, résumé auto-généré. Comparez à la moyenne du poste." },
  { href: "/tactique", icon: "🧠", title: "Score Tactique",   desc: "Score 0–100 de compatibilité avec 4 styles de jeu.", accent: true },
  { href: "/video",    icon: "🎬", title: "Analyse Vidéo",    desc: "Upload clip · overlay vitesse/trajectoire/zones · export enrichi.", cyan: true },
  { href: "/heatmap",  icon: "🔥", title: "Heatmap",          desc: "Zones d'activité filtrables par période et type d'action." },
  { href: "/match",    icon: "📊", title: "Analyse Match",    desc: "xG timeline, shot map, réseau de passes, événements clés." },
  { href: "/fbref",    icon: "📡", title: "Données Live",     desc: "Stats FBref saison en cours — joueurs, équipes, xG, tirs, passes." },
  { href: "/rapport",  icon: "📄", title: "Rapport PDF",      desc: "Export PDF brandé avec heatmap, radar et observations tactiques." },
];

const METRICS = [
  { label: "Compétitions",  value: "44+",    delta: "StatsBomb Open", up: true  },
  { label: "KPIs tactiques",value: "30+",    delta: "Par match",      up: false },
  { label: "Score tactique",value: "0–100",  delta: "4 styles de jeu",up: false },
  { label: "Données live",  value: "FBref",  delta: "2024–2025",      up: true  },
];

export default function HomePage() {
  return (
    <div style={{ padding: "28px 32px" }}>
      <TopBar title="⚽ la soccer Machine" badge="v2.0 · SaaS" />

      {/* Hero */}
      <div style={{ textAlign: "center", padding: "32px 20px 28px" }}>
        <div style={{
          width: "90px", height: "90px", margin: "0 auto 18px",
          background: "#111a13", border: "2px solid rgba(57,255,106,0.3)",
          borderRadius: "18px", display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: "2.5rem",
          boxShadow: "0 0 40px rgba(57,255,106,0.12)",
        }}>⚽</div>
        <h2 className="text-grad" style={{ fontSize: "2rem", fontWeight: 800 }}>la soccer Machine</h2>
        <p style={{ color: "#7a9e82", marginTop: "10px", maxWidth: "540px", margin: "10px auto 0", fontSize: "0.92rem", lineHeight: 1.65 }}>
          Plateforme d&apos;analyse tactique professionnelle. Données StatsBomb + <strong style={{ color: "#00e5ff" }}>FBref live</strong> + analyse vidéo avec overlays.
        </p>
        <Link href="/profil" style={{
          display: "inline-block", marginTop: "20px",
          background: "linear-gradient(135deg, #39ff6a, #00e5ff)",
          color: "#080c0a", fontWeight: 800, borderRadius: "8px",
          padding: "12px 32px", fontSize: "0.9rem", textDecoration: "none",
          letterSpacing: "0.04em",
        }}>👤 Analyser un joueur →</Link>
      </div>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "14px", marginBottom: "22px" }}>
        {METRICS.map(m => (
          <div key={m.label} style={{
            background: "#111a13", border: "1px solid rgba(57,255,106,0.18)",
            borderRadius: "10px", padding: "14px 18px", position: "relative", overflow: "hidden",
          }}>
            <div style={{ fontSize: "0.68rem", color: "#7a9e82", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "5px" }}>{m.label}</div>
            <div style={{ fontSize: "1.7rem", fontWeight: 700, color: "#e2ede5", lineHeight: 1 }}>{m.value}</div>
            <div style={{ fontSize: "0.72rem", color: m.up ? "#39ff6a" : "#7a9e82", marginTop: "4px" }}>{m.delta}</div>
          </div>
        ))}
      </div>

      {/* Feature grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "14px" }}>
        {FEATURES.map(f => (
          <Link key={f.href} href={f.href} style={{
            background: "#111a13",
            border: `1px solid ${f.cyan ? "rgba(0,229,255,0.3)" : "rgba(57,255,106,0.18)"}`,
            borderRadius: "12px", padding: "18px", textAlign: "center",
            textDecoration: "none", display: "block", transition: "border-color 0.2s",
          }}>
            <div style={{ fontSize: "1.8rem", marginBottom: "8px" }}>{f.icon}</div>
            <h3 style={{ fontSize: "0.82rem", color: f.cyan ? "#00e5ff" : "#39ff6a", marginBottom: "5px", fontWeight: 700 }}>{f.title}</h3>
            <p style={{ fontSize: "0.75rem", color: "#7a9e82", lineHeight: 1.5 }}>{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
