"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { socialApi } from "@/lib/social-api"

export default function NewMatchPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    opponent_name: "", home_score: "", away_score: "",
    match_date: new Date().toISOString().slice(0, 10),
    competition: "", is_home: true,
    goals: "0", assists: "0", shots: "0", key_passes: "0",
    player_rating: "7",
  })
  const [loading, setLoading] = useState(false)

  function field(key: keyof typeof form) {
    return {
      value: form[key] as string,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setForm(f => ({ ...f, [key]: e.target.value })),
    }
  }

  const inputStyle = {
    width: "100%", background: "#17182A", color: "#F2F4FF",
    border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12,
    padding: "12px 14px", fontSize: "0.85rem", outline: "none",
    fontFamily: "'Outfit', sans-serif",
  }

  const labelStyle = {
    fontSize: "0.68rem", color: "#7B8098", fontWeight: 700 as const,
    textTransform: "uppercase" as const, letterSpacing: "0.07em", display: "block" as const, marginBottom: 6,
  }

  async function submit() {
    if (!form.opponent_name || !form.match_date) return
    setLoading(true)
    try {
      await socialApi.createMatch({
        opponent_name: form.opponent_name,
        home_score: form.home_score ? Number(form.home_score) : undefined,
        away_score: form.away_score ? Number(form.away_score) : undefined,
        match_date: form.match_date,
        competition: form.competition || undefined,
        is_home: form.is_home,
      })
      router.push("/profil-social")
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  return (
    <div style={{ padding: "20px 16px", fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: "1.2rem", fontWeight: 900, color: "#F2F4FF" }}>Ajouter un match</div>
        <div style={{ fontSize: "0.72rem", color: "#7B8098" }}>Enrichis ton profil avec tes performances</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <label style={labelStyle}>Adversaire *</label>
          <input {...field("opponent_name")} type="text" placeholder="Nom de l'équipe adverse" style={inputStyle} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label style={labelStyle}>Score (nous)</label>
            <input {...field("home_score")} type="number" min="0" placeholder="2" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Score (eux)</label>
            <input {...field("away_score")} type="number" min="0" placeholder="1" style={inputStyle} />
          </div>
        </div>
        <div>
          <label style={labelStyle}>Date *</label>
          <input {...field("match_date")} type="date" style={inputStyle} />
        </div>
        <div>
          <label style={labelStyle}>Compétition</label>
          <input {...field("competition")} type="text" placeholder="Ligue Martinique J12" style={inputStyle} />
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 16 }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#F2F4FF", marginBottom: 14 }}>Mes stats</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div><label style={labelStyle}>Buts</label><input {...field("goals")} type="number" min="0" style={inputStyle} /></div>
            <div><label style={labelStyle}>Passes déc.</label><input {...field("assists")} type="number" min="0" style={inputStyle} /></div>
            <div><label style={labelStyle}>Tirs</label><input {...field("shots")} type="number" min="0" style={inputStyle} /></div>
            <div><label style={labelStyle}>Passes clés</label><input {...field("key_passes")} type="number" min="0" style={inputStyle} /></div>
          </div>
          <div style={{ marginTop: 12 }}>
            <label style={labelStyle}>Ma note : {form.player_rating}/10</label>
            <input type="range" min="1" max="10" step="0.5"
              value={form.player_rating}
              onChange={e => setForm(f => ({ ...f, player_rating: e.target.value }))}
              style={{ width: "100%", accentColor: "#C8FF57" }}
            />
          </div>
        </div>
        <button onClick={submit} disabled={loading} style={{
          width: "100%", background: loading ? "rgba(200,255,87,0.3)" : "#C8FF57",
          color: "#0E0F18", border: "none", borderRadius: 100, padding: 14,
          fontWeight: 800, fontSize: "0.9rem",
          cursor: loading ? "not-allowed" : "pointer",
          fontFamily: "'Outfit', sans-serif",
        }}>
          {loading ? "Enregistrement..." : "⚽ Enregistrer le match"}
        </button>
      </div>
    </div>
  )
}
