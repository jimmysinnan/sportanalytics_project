"use client"
import { useEffect, useState } from "react"
import { socialApi } from "@/lib/social-api"
import type { RankingRow, PlayerRanking } from "@/lib/social-types"

const TIER_COLORS: Record<string, string> = {
  silver: "#C8C8D8", gold: "#FFE566", elite: "#FF8080", legend: "#D080FF",
}

export default function ClassementsPage() {
  const [rows, setRows] = useState<RankingRow[]>([])
  const [myRanking, setMyRanking] = useState<PlayerRanking | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      socialApi.rankings({ limit: 50 }).then(setRows),
      socialApi.myRanking().then(r => setMyRanking(r)),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: 24, textAlign: "center", color: "#7B8098", paddingTop: 60, fontFamily: "'Outfit', sans-serif" }}>
      Chargement...
    </div>
  )

  return (
    <div style={{ padding: "16px 0 0", fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ padding: "0 16px 16px" }}>
        <div style={{ fontSize: "1.1rem", fontWeight: 900, color: "#F2F4FF" }}>Classements</div>
        <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>Classement local par poste et région</div>
      </div>

      {myRanking && (
        <div style={{
          margin: "0 16px 16px",
          background: "linear-gradient(135deg,#0d1020,#131428)",
          borderRadius: 16, padding: 16,
          border: "1px solid rgba(68,136,255,0.2)",
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <div>
            <div style={{ fontSize: "2.2rem", fontWeight: 900, color: "#FFD60A", lineHeight: 1 }}>
              #{myRanking.rank}
            </div>
            <div style={{ fontSize: "0.72rem", color: "#b0b8cc", marginTop: 4 }}>
              {myRanking.position ?? "Tous postes"} · {myRanking.region ?? "Global"}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: "0.65rem", color: "#7B8098", marginBottom: 5 }}>
              Top {(100 - Math.round(myRanking.percentile))}% · {myRanking.total_players} joueurs
            </div>
            <div style={{ height: 5, background: "rgba(255,255,255,0.06)", borderRadius: 3, overflow: "hidden" }}>
              <div style={{
                height: "100%", width: `${myRanking.percentile}%`,
                background: "linear-gradient(90deg,#FFD60A,#FF9800)", borderRadius: 3,
              }} />
            </div>
          </div>
        </div>
      )}

      {rows.map(row => (
        <div key={row.player_id} style={{
          margin: "0 16px 4px", background: "#17182A", borderRadius: 12,
          padding: "10px 14px", display: "flex", alignItems: "center", gap: 10,
          border: "1px solid rgba(255,255,255,0.04)",
        }}>
          <div style={{
            width: 24, textAlign: "center", fontSize: "0.8rem", fontWeight: 700,
            color: row.rank <= 3 ? "#FFD60A" : "#7B8098",
          }}>{row.rank}</div>
          <div style={{
            width: 34, height: 34, borderRadius: "50%",
            background: "linear-gradient(135deg,#1a2030,#0d1020)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "0.9rem", border: "1.5px solid rgba(255,255,255,0.07)", flexShrink: 0, overflow: "hidden",
          }}>
            {row.photo_url
              ? <img src={row.photo_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              : "⚽"}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#F2F4FF" }}>{row.name}</div>
            <div style={{ fontSize: "0.62rem", color: "#7B8098", marginTop: 1 }}>
              {row.position_short} · {row.club ?? "—"}
            </div>
          </div>
          <div style={{ fontSize: "1rem", fontWeight: 800, color: TIER_COLORS[row.machine_score_tier] ?? "#F2F4FF" }}>
            {row.machine_score}
          </div>
        </div>
      ))}

      {rows.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "40px 20px", color: "#7B8098" }}>
          <p style={{ fontSize: "0.85rem" }}>Aucun joueur dans ce classement pour l&apos;instant.</p>
        </div>
      )}
    </div>
  )
}
