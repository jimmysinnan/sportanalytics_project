"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import type { FeedPost } from "@/lib/social-types"

const POST_LABELS: Record<string, string> = {
  match_added: "a ajouté un match",
  votm: "a été élu joueur du match",
  card_upgrade: "a upgradé sa Player Card",
}

export default function FeedPage() {
  const [posts, setPosts] = useState<FeedPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    socialApi.feed().then(setPosts).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60, fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ fontSize: "2rem", marginBottom: 12 }}>⚽</div>
      Chargement...
    </div>
  )

  return (
    <div style={{ padding: "16px 0 0", fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ padding: "0 16px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF", letterSpacing: "-0.02em" }}>
            Orbyon Sport
          </div>
          <div style={{ fontSize: "0.72rem", color: "#7B8098", fontWeight: 600 }}>
            Activité de ta communauté
          </div>
        </div>
        <span style={{ fontSize: "1.2rem" }}>🔔</span>
      </div>

      {posts.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#7B8098" }}>
          <div style={{ fontSize: "3rem", marginBottom: 12 }}>🏟️</div>
          <p style={{ fontSize: "0.88rem" }}>Aucune activité.<br />Ajoute ton premier match !</p>
        </div>
      ) : (
        posts.map(post => (
          <div key={post.id} style={{
            margin: "0 16px 10px",
            background: "#17182A",
            borderRadius: 18, padding: 14,
            border: "1px solid rgba(255,255,255,0.05)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{
                width: 36, height: 36, borderRadius: "50%",
                background: "linear-gradient(135deg,#252840,#151628)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "0.9rem", border: "1.5px solid rgba(200,255,87,0.15)", flexShrink: 0,
                overflow: "hidden",
              }}>
                {post.player_photo_url
                  ? <img src={post.player_photo_url} alt="" style={{ width: "100%", height: "100%", borderRadius: "50%", objectFit: "cover" }} />
                  : "⚽"}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "0.82rem", fontWeight: 800, color: "#F2F4FF" }}>{post.player_name}</div>
                <div style={{ fontSize: "0.65rem", color: "#7B8098", marginTop: 1 }}>
                  {POST_LABELS[post.post_type] ?? post.post_type}
                </div>
              </div>
              <div style={{ fontSize: "0.62rem", color: "#3D4060" }}>
                {new Date(post.created_at).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" })}
              </div>
            </div>
            {post.content && post.post_type === "match_added" && (
              <div style={{
                background: "rgba(200,255,87,0.06)", borderRadius: 10, padding: "8px 12px",
                fontSize: "0.8rem", color: "#b0b8cc", border: "1px solid rgba(200,255,87,0.1)",
              }}>
                ⚽ vs <strong style={{ color: "#F2F4FF" }}>{String(post.content.opponent ?? "")}</strong>
                {post.content.score ? ` — ${post.content.score}` : ""}
              </div>
            )}
            <button
              onClick={() => socialApi.likePost(post.id).catch(console.error)}
              style={{
                marginTop: 8, fontSize: "0.72rem", color: "#7B8098",
                background: "rgba(255,255,255,0.04)", border: "none",
                borderRadius: 100, padding: "5px 12px", cursor: "pointer",
                fontFamily: "'Outfit', sans-serif", fontWeight: 600,
              }}
            >
              Réagir {post.likes_count > 0 ? post.likes_count : ""}
            </button>
          </div>
        ))
      )}
    </div>
  )
}
