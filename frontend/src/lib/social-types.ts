export type Tier = "silver" | "gold" | "elite" | "legend"

export interface SocialPlayer {
  id: string
  name: string
  username: string
  position: string | null
  position_short: string | null
  club: string | null
  region: string | null
  category: string | null
  country_code: string | null
  photo_url: string | null
  machine_score: number
  machine_score_tier: Tier
  data_level: 1 | 2 | 3
}

export interface MatchLog {
  id: string
  opponent_name: string
  home_score: number | null
  away_score: number | null
  match_date: string
  competition: string | null
  is_home: boolean
}

export interface FeedPost {
  id: string
  post_type: string
  content: Record<string, unknown> | null
  likes_count: number
  created_at: string
  player_name: string
  player_username: string
  player_photo_url: string | null
  player_score: number
  player_tier: Tier
}

export interface RankingRow {
  rank: number
  percentile: number
  player_id: string
  name: string
  username: string
  position_short: string | null
  club: string | null
  machine_score: number
  machine_score_tier: Tier
  photo_url: string | null
}

export interface PlayerRanking {
  rank: number
  percentile: number
  total_players: number
  position: string | null
  region: string | null
  category: string | null
}

export interface VoteRequest {
  voted_for_id: string
  is_votm: boolean
  badges: string[]
}
