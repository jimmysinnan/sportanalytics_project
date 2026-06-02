"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/",         icon: "🏠", label: "Accueil" },
  { href: "/profil",   icon: "👤", label: "Profil Joueur" },
  { href: "/heatmap",  icon: "🔥", label: "Heatmap" },
  { href: "/match",    icon: "📊", label: "Analyse Match" },
  { href: "/tactique", icon: "🧠", label: "Score Tactique" },
  { href: "/video",    icon: "🎬", label: "Analyse Vidéo", badge: "NEW" },
  { href: "/fbref",    icon: "📡", label: "Données Live" },
  { href: "/rapport",  icon: "📄", label: "Rapport PDF" },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <nav style={{
      width: "220px", minWidth: "220px",
      background: "#0d1510",
      borderRight: "1px solid rgba(57,255,106,0.18)",
      display: "flex", flexDirection: "column",
      height: "100vh", position: "sticky", top: 0,
      paddingBottom: "20px", overflowY: "auto",
    }}>
      {/* Brand */}
      <div style={{
        padding: "24px 18px 18px",
        borderBottom: "1px solid rgba(57,255,106,0.18)",
        display: "flex", alignItems: "center", gap: "12px",
      }}>
        <div style={{
          width: "44px", height: "44px", flexShrink: 0,
          background: "linear-gradient(135deg, #0d1510, #1a2e1e)",
          border: "1.5px solid rgba(57,255,106,0.4)",
          borderRadius: "10px",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "1.35rem",
          boxShadow: "0 0 14px rgba(57,255,106,0.15)",
        }}>⚽</div>
        <div>
          <div className="text-grad" style={{ fontSize: "0.88rem", fontWeight: 800, lineHeight: 1.2 }}>
            la soccer<br />Machine
          </div>
          <div style={{ fontSize: "0.6rem", color: "#7a9e82", letterSpacing: "0.12em", textTransform: "uppercase", marginTop: "1px" }}>
            Analytics
          </div>
        </div>
      </div>

      {/* Nav */}
      <div style={{ padding: "16px 10px", flex: 1, display: "flex", flexDirection: "column", gap: "3px" }}>
        {NAV.map(({ href, icon, label, badge }) => {
          const active = path === href;
          return (
            <Link
              key={href}
              href={href}
              style={{
                display: "flex", alignItems: "center", gap: "10px",
                padding: "9px 12px", borderRadius: "8px",
                fontSize: "0.82rem", textDecoration: "none",
                color: active ? "#39ff6a" : "#7a9e82",
                background: active ? "rgba(57,255,106,0.1)" : "transparent",
                border: `1px solid ${active ? "rgba(57,255,106,0.2)" : "transparent"}`,
                transition: "all 0.15s",
              }}
              onMouseEnter={e => {
                if (!active) {
                  (e.currentTarget as HTMLAnchorElement).style.background = "rgba(57,255,106,0.06)";
                  (e.currentTarget as HTMLAnchorElement).style.color = "#e2ede5";
                }
              }}
              onMouseLeave={e => {
                if (!active) {
                  (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
                  (e.currentTarget as HTMLAnchorElement).style.color = "#7a9e82";
                }
              }}
            >
              <span style={{ fontSize: "1rem", width: "20px", textAlign: "center", flexShrink: 0 }}>{icon}</span>
              <span style={{ flex: 1 }}>{label}</span>
              {badge && (
                <span style={{
                  background: "linear-gradient(135deg, #39ff6a, #00e5ff)",
                  color: "#080c0a", fontSize: "0.55rem", fontWeight: 800,
                  padding: "2px 6px", borderRadius: "20px", letterSpacing: "0.05em",
                }}>{badge}</span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{ padding: "0 18px", fontSize: "0.67rem", color: "#7a9e82", opacity: 0.5 }}>
        <div>StatsBomb Open Data</div>
        <div>FBref Live Data</div>
        <div style={{ marginTop: "3px" }}>© 2026 la soccer Machine</div>
      </div>
    </nav>
  );
}
