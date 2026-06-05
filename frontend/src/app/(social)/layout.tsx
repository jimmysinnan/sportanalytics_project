"use client"
import { usePathname } from "next/navigation"
import Link from "next/link"

const NAV = [
  { href: "/feed",          icon: "🏠", label: "Feed" },
  { href: "/profil-social", icon: "👤", label: "Profil" },
  { href: "/match/new",     icon: "+",  label: "",      isAdd: true },
  { href: "/classements",   icon: "🏆", label: "Clsmt" },
  { href: "/equipe",        icon: "⚽", label: "Équipe" },
]

export default function SocialLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname()
  return (
    <div style={{
      maxWidth: 480, margin: "0 auto", minHeight: "100dvh",
      background: "#0E0F18", display: "flex", flexDirection: "column",
      position: "relative",
    }}>
      <div style={{ flex: 1, overflowY: "auto", paddingBottom: 80 }}>
        {children}
      </div>
      <nav style={{
        position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)",
        width: "100%", maxWidth: 480,
        height: 72, background: "rgba(14,15,24,0.96)",
        backdropFilter: "blur(20px)",
        borderTop: "1px solid rgba(255,255,255,0.05)",
        display: "flex", alignItems: "flex-start", justifyContent: "space-around",
        paddingTop: 10, zIndex: 100,
      }}>
        {NAV.map(({ href, icon, label, isAdd }) => {
          const active = path === href
          if (isAdd) return (
            <Link key={href} href={href} style={{
              width: 52, height: 44, background: "#C8FF57",
              borderRadius: 100, display: "flex",
              alignItems: "center", justifyContent: "center",
              fontSize: "1.5rem", color: "#0E0F18", fontWeight: 900,
              marginTop: -12, boxShadow: "0 4px 20px rgba(200,255,87,0.35)",
              textDecoration: "none",
            }}>+</Link>
          )
          return (
            <Link key={href} href={href} style={{
              display: "flex", flexDirection: "column", alignItems: "center", gap: 3,
              textDecoration: "none",
              color: active ? "#C8FF57" : "#7B8098",
              fontSize: "0.55rem", fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.07em",
            }}>
              <span style={{ fontSize: "1.1rem" }}>{icon}</span>
              <span>{label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
