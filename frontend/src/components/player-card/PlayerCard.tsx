"use client"
import { TIER_CONFIG } from "./PlayerCardTiers"
import type { Tier } from "@/lib/social-types"

export interface PlayerCardAttributes {
  tec: number; phy: number; vit: number
  def: number; vis: number; imp: number
}

interface Props {
  score: number
  tier: Tier
  positionShort: string
  name: string
  photoUrl?: string | null
  countryCode?: string | null
  clubEmoji?: string
  attributes: PlayerCardAttributes
  size?: "sm" | "md" | "lg"
  onPhotoClick?: () => void
}

const SIZES = {
  sm:  { w: 140, h: 200, score: "1.6rem", name: "0.65rem", stat: "0.52rem" },
  md:  { w: 200, h: 290, score: "2.4rem", name: "0.9rem",  stat: "0.7rem"  },
  lg:  { w: 280, h: 406, score: "3.2rem", name: "1.2rem",  stat: "0.9rem"  },
}

const FLAG_MAP: Record<string, string> = {
  MQ: "🇲🇶", FR: "🇫🇷", BR: "🇧🇷", NG: "🇳🇬", CM: "🇨🇲",
  SN: "🇸🇳", CI: "🇨🇮", MA: "🇲🇦", DZ: "🇩🇿", ES: "🇪🇸",
  PT: "🇵🇹", GB: "🇬🇧", DE: "🇩🇪", IT: "🇮🇹", AR: "🇦🇷",
}

export default function PlayerCard({
  score, tier, positionShort, name, photoUrl, countryCode,
  clubEmoji = "⚽", attributes, size = "md", onPhotoClick,
}: Props) {
  const cfg = TIER_CONFIG[tier]
  const sz = SIZES[size]
  const flag = countryCode ? (FLAG_MAP[countryCode.toUpperCase()] ?? "🌍") : "🌍"
  const attrs: { val: number; lbl: string }[] = [
    { val: attributes.tec, lbl: "TEC" },
    { val: attributes.phy, lbl: "PHY" },
    { val: attributes.vit, lbl: "VIT" },
    { val: attributes.def, lbl: "DEF" },
    { val: attributes.vis, lbl: "VIS" },
    { val: attributes.imp, lbl: "IMP" },
  ]
  const displayName = name.split(" ").map((w, i) => i === 0 ? w[0] + "." : w).join(" ")

  return (
    <div style={{
      width: sz.w, height: sz.h,
      background: cfg.bgGradient,
      borderRadius: 14,
      border: `1.5px solid ${cfg.borderColor}`,
      boxShadow: `0 12px 40px ${cfg.shadowColor}, 0 0 0 1px ${cfg.accentColor}22`,
      position: "relative", overflow: "hidden",
      display: "flex", flexDirection: "column",
      fontFamily: "'Outfit', sans-serif",
    }}>
      {/* Score + flags */}
      <div style={{ display: "flex", alignItems: "flex-start", padding: "10px 10px 0", gap: 6 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <span style={{
            fontFamily: "Oswald, 'Outfit', sans-serif",
            fontSize: sz.score, fontWeight: 700, lineHeight: 1,
            color: cfg.scoreColor,
          }}>{score}</span>
          <span style={{
            fontSize: `calc(${sz.stat} * 1.1)`, fontWeight: 800,
            color: cfg.scoreColor, opacity: 0.85,
            letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 1,
          }}>{positionShort}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 2 }}>
          <span style={{ fontSize: size === "sm" ? "0.75rem" : "0.9rem" }}>{flag}</span>
          <span style={{ fontSize: size === "sm" ? "0.7rem" : "0.85rem" }}>{clubEmoji}</span>
        </div>
      </div>

      {/* Photo */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {photoUrl ? (
          <img src={photoUrl} alt={name} style={{
            width: "100%", height: "100%",
            objectFit: "cover", objectPosition: "top center",
          }} />
        ) : (
          <div onClick={onPhotoClick} style={{
            width: "100%", height: "100%",
            display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
            gap: 6, cursor: onPhotoClick ? "pointer" : "default",
          }}>
            <div style={{
              width: size === "sm" ? 44 : 60, height: size === "sm" ? 44 : 60,
              borderRadius: "50%", border: `2px dashed ${cfg.accentColor}`,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
            }}>
              <span style={{ fontSize: size === "sm" ? "1rem" : "1.4rem", opacity: 0.5 }}>📷</span>
            </div>
            {size !== "sm" && (
              <span style={{ fontSize: "0.6rem", color: "rgba(255,255,255,0.35)", textAlign: "center", fontWeight: 600 }}>
                Ajouter ma photo
              </span>
            )}
          </div>
        )}
        {/* Fade */}
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 0, height: "60%",
          background: `linear-gradient(transparent, ${cfg.fadeTo} 90%)`,
          pointerEvents: "none",
        }} />
      </div>

      {/* Name */}
      <div style={{
        fontFamily: "Oswald, 'Outfit', sans-serif",
        fontSize: sz.name, fontWeight: 700,
        textAlign: "center", padding: "0 8px",
        textTransform: "uppercase", letterSpacing: "0.08em",
        color: "#fff", textShadow: "0 2px 6px rgba(0,0,0,0.8)",
        position: "relative", zIndex: 2, marginTop: -4,
        whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
      }}>{displayName}</div>

      {/* Divider */}
      <div style={{
        height: 1, margin: `4px ${size === "sm" ? 8 : 12}px`,
        background: cfg.accentColor, opacity: 0.5,
      }} />

      {/* Stats 3x2 */}
      <div style={{
        display: "grid", gridTemplateColumns: "1fr 1fr 1fr",
        padding: `0 ${size === "sm" ? 6 : 10}px ${size === "sm" ? 8 : 12}px`,
      }}>
        {attrs.map(({ val, lbl }) => (
          <div key={lbl} style={{ textAlign: "center", padding: "2px 0" }}>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: sz.stat, fontWeight: 600, color: "rgba(255,255,255,0.9)",
            }}>{val}</div>
            <div style={{
              fontSize: `calc(${sz.stat} * 0.75)`,
              color: cfg.scoreColor, opacity: 0.7,
              textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700,
            }}>{lbl}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
