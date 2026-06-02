import type {
  Competition,
  Match,
  PlayerStatsResponse,
  MatchSummary,
  TacticalReport,
  FBrefPlayer,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  competitions: (): Promise<{ competitions: Competition[] }> =>
    get("/competitions/"),

  matches: (compId: number, seasonId: number): Promise<{ matches: Match[] }> =>
    get(`/competitions/${compId}/seasons/${seasonId}/matches`),

  players: (matchId: number): Promise<{ players: string[] }> =>
    get(`/players/${matchId}/list`),

  playerStats: (matchId: number, player: string): Promise<PlayerStatsResponse> =>
    get(`/players/${matchId}/${encodeURIComponent(player)}/stats`),

  heatmap: (
    matchId: number,
    player: string,
    action = "all",
    period = "full"
  ): Promise<{ image_b64: string }> =>
    get(
      `/players/${matchId}/${encodeURIComponent(player)}/heatmap?action_type=${action}&period=${period}`
    ),

  radar: (matchId: number, player: string): Promise<{ image_b64: string }> =>
    get(`/players/${matchId}/${encodeURIComponent(player)}/radar`),

  matchSummary: (matchId: number): Promise<MatchSummary> =>
    get(`/match/${matchId}/summary`),

  shotMap: (matchId: number, team: string): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/shots/${encodeURIComponent(team)}`),

  xgTimeline: (matchId: number): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/xg-timeline`),

  passNetwork: (
    matchId: number,
    team: string
  ): Promise<{ image_b64: string }> =>
    get(`/match/${matchId}/pass-network/${encodeURIComponent(team)}`),

  lineups: (matchId: number): Promise<Record<string, object[]>> =>
    get(`/match/${matchId}/lineups`),

  tacticalScore: (body: {
    match_id: number;
    player_name: string;
    player_position: string;
    team_style: string;
    phase_config: Record<string, string>;
  }): Promise<TacticalReport> => post("/tactical/score", body),

  downloadPdf: async (body: {
    match_id: number;
    player_name: string;
    position: string;
    competition_label: string;
    observations: string;
  }): Promise<Blob> => {
    const res = await fetch(`${BASE}/pdf/player`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`PDF generation failed: ${res.status}`);
    return res.blob();
  },

  fbrefLeagues: (): Promise<{
    leagues: Record<string, string>;
    seasons: string[];
  }> => get("/fbref/leagues"),

  fbrefPlayers: (
    league: string,
    season: string
  ): Promise<{ players: FBrefPlayer[]; total: number }> =>
    get(`/fbref/${encodeURIComponent(league)}/players?season=${season}`),
};
