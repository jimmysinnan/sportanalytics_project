"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import PlayerCard from "@/components/player-card/PlayerCard"
import PhotoUpload from "@/components/player-card/PhotoUpload"
import type { SocialPlayer } from "@/lib/social-types"
import type { PlayerCardAttributes } from "@/components/player-card/PlayerCard"

export default function ProfilSocialPage() {
  const [player, setPlayer] = useState<SocialPlayer | null>(null)
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    socialApi.me().then(setPlayer).catch(console.error).finally(() => setLoading(false))
  }, [])

  async function handlePhoto(file: File) {
    setUploading(true)
    try { const updated = await socialApi.uploadPhoto(file); setPlayer(updated) }
    catch (e) { console.error(e) }
    setUploading(false)
  }

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60, fontFamily: "'Outfit', sans-serif" }}>
      Chargement...
    </div>
  )

  if (!player) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60, fontFamily: "'Outfit', sans-serif" }}>
      <p>Non connecté. <a href="/auth/login" style={{ color: "#C8FF57" }}>Se connecter</a></p>
    </div>
  )

  const attrs: PlayerCardAttributes = {
    tec: 60, phy: 60, vit: 60, def: 60, vis: 60,
    imp: Math.min(player.machine_score, 99),
  }

  return (
    <div style={{ padding: "16px 16px 0", fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF" }}>Mon Profil</div>
          <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>@{player.username}</div>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
        <PlayerCard
          score={player.machine_score}
          tier={player.machine_score_tier}
          positionShort={player.position_short ?? "?"}
          name={player.name}
          photoUrl={player.photo_url}
          countryCode={player.country_code ?? undefined}
          attributes={attrs}
          size="lg"
          onPhotoClick={() => setShowUpload(true)}
        />
      </div>

      {!player.photo_url && (
        <div style={{
          background: "rgba(200,255,87,0.06)", borderRadius: 14,
          padding: "12px 16px", marginBottom: 16,
          border: "1px solid rgba(200,255,87,0.15)",
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <span style={{ fontSize: "1.2rem" }}>📷</span>
          <div style={{ flex: 1, fontSize: "0.82rem", color: "#b0b8cc" }}>
            Ajoute ta photo pour activer ta Player Card
          </div>
          <button
            onClick={() => setShowUpload(true)}
            style={{
              background: "#C8FF57", color: "#0E0F18", border: "none",
              borderRadius: 100, padding: "6px 14px", fontWeight: 800,
              fontSize: "0.72rem", cursor: "pointer", fontFamily: "'Outfit'",
            }}
          >+ Photo</button>
        </div>
      )}

      <div style={{
        display: "flex", background: "#17182A", borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.05)", marginBottom: 16, overflow: "hidden",
      }}>
        {[
          { val: player.machine_score, lbl: "Score" },
          { val: "—", lbl: "Matchs" },
          { val: "—", lbl: "Buts" },
          { val: "—", lbl: "Note" },
        ].map(({ val, lbl }, i) => (
          <div key={lbl} style={{
            flex: 1, padding: "12px 8px", textAlign: "center",
            borderLeft: i > 0 ? "1px solid rgba(255,255,255,0.05)" : "none",
          }}>
            <div style={{ fontSize: "1.2rem", fontWeight: 800, color: "#F2F4FF", fontFamily: "'JetBrains Mono', monospace" }}>{val}</div>
            <div style={{ fontSize: "0.52rem", color: "#7B8098", textTransform: "uppercase", letterSpacing: "0.1em", marginTop: 3, fontWeight: 700 }}>{lbl}</div>
          </div>
        ))}
      </div>

      <button style={{
        width: "100%", background: "transparent",
        border: "1.5px solid rgba(200,255,87,0.3)", color: "#C8FF57",
        borderRadius: 100, padding: 12, fontWeight: 800,
        fontSize: "0.82rem", cursor: "pointer", fontFamily: "'Outfit'",
      }}>
        Partager mon profil
      </button>

      {showUpload && <PhotoUpload onFile={handlePhoto} onClose={() => setShowUpload(false)} />}
      {uploading && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 999, color: "#C8FF57", fontSize: "0.9rem", fontWeight: 700, fontFamily: "'Outfit'",
        }}>Envoi en cours...</div>
      )}
    </div>
  )
}
