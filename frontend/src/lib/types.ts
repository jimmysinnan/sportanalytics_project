export interface Competition {
  competition_id: number;
  season_id: number;
  competition_name: string;
  season_name: string;
  country_name?: string;
}

export interface Match {
  match_id: number;
  label: string;
  home_team: string;
  away_team: string;
  home_score: string | number;
  away_score: string | number;
  match_date: string;
}

export interface PlayerMetrics {
  minutes: number;
  goals: number;
  assists: number;
  passes: number;
  pass_completion: number;
  pressures: number;
  duels: number;
  duels_won: number;
  xg: number;
  shots: number;
  shots_on_target: number;
  progressive_passes: number;
  pressing_intensity: number;
  defensive_actions: number;
  dribbles_completed: number;
  dribbles_attempted: number;
  key_passes: number;
  carries: number;
  ball_receipts: number;
  [key: string]: number;
}

export interface PlayerStatsResponse {
  metrics: PlayerMetrics;
  position: string;
  summary: string;
}

export interface MatchSummary {
  home_team: string;
  away_team: string;
  home_possession: number;
  away_possession: number;
  home_shots: number;
  away_shots: number;
  home_passes: number;
  away_passes: number;
  home_xg: number;
  away_xg: number;
}

export interface TacticalReport {
  player_name: string;
  match_id: number;
  tactical_compatibility_score: number;
  pressing_triggers: number;
  vertical_passes_ratio: number;
  counterpressing_efficiency: number;
  versatility_score: number;
  false_nine_drops: number;
  half_space_runs: number;
  distance_estimate_km: number;
  possession_share: number;
  tactical_feedback: string[];
}

export interface FBrefPlayer {
  player: string;
  team: string;
  pos?: string;
  age?: number;
  games?: number;
  goals?: number;
  assists?: number;
  xg?: number;
  [key: string]: string | number | undefined;
}
