import { getToken } from "./auth"
import type {
  SocialPlayer, MatchLog, FeedPost, RankingRow, PlayerRanking, VoteRequest,
} from "./social-types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function authFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getToken()
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers as Record<string, string> ?? {}),
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error((err as { detail?: string }).detail ?? `API ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const socialApi = {
  register: (body: {
    name: string; username: string; position?: string
    club?: string; region?: string; category?: string; country_code?: string
  }): Promise<SocialPlayer> =>
    authFetch("/players/register", { method: "POST", body: JSON.stringify(body) }),

  me: (): Promise<SocialPlayer> =>
    authFetch("/players/me"),

  updateMe: (body: Partial<Pick<SocialPlayer, "name" | "position" | "club" | "region" | "category" | "country_code">>): Promise<SocialPlayer> =>
    authFetch("/players/me", { method: "PATCH", body: JSON.stringify(body) }),

  uploadPhoto: async (file: File): Promise<SocialPlayer> => {
    const token = await getToken()
    const form = new FormData()
    form.append("file", file)
    const res = await fetch(`${BASE}/players/me/photo`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    })
    if (!res.ok) throw new Error("Upload photo échoué")
    return res.json() as Promise<SocialPlayer>
  },

  getPlayer: (username: string): Promise<SocialPlayer> =>
    authFetch(`/players/${encodeURIComponent(username)}`),

  createMatch: (body: {
    opponent_name: string; home_score?: number; away_score?: number
    match_date: string; competition?: string; is_home?: boolean
    team_id?: string; players?: object[]
  }): Promise<MatchLog> =>
    authFetch("/matches", { method: "POST", body: JSON.stringify(body) }),

  myMatches: (): Promise<MatchLog[]> =>
    authFetch("/matches/me"),

  vote: (matchId: string, body: VoteRequest): Promise<{ status: string }> =>
    authFetch(`/matches/${matchId}/vote`, { method: "POST", body: JSON.stringify(body) }),

  feed: (offset = 0): Promise<FeedPost[]> =>
    authFetch(`/feed?offset=${offset}`),

  likePost: (postId: string): Promise<void> =>
    authFetch(`/feed/${postId}/like`, { method: "POST" }),

  myRanking: (): Promise<PlayerRanking | null> =>
    authFetch("/rankings/me"),

  rankings: (params: {
    region?: string; category?: string; position?: string; limit?: number
  } = {}): Promise<RankingRow[]> => {
    const q = new URLSearchParams()
    if (params.region) q.set("region", params.region)
    if (params.category) q.set("category", params.category)
    if (params.position) q.set("position", params.position)
    if (params.limit) q.set("limit", String(params.limit))
    return authFetch(`/rankings?${q.toString()}`)
  },
}
