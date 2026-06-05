import type { Tier } from "@/lib/social-types"

export interface TierConfig {
  bgGradient: string
  accentColor: string
  borderColor: string
  shadowColor: string
  scoreColor: string
  fadeTo: string
}

export const TIER_CONFIG: Record<Tier, TierConfig> = {
  silver: {
    bgGradient: "linear-gradient(160deg, #1a1a1a 0%, #2d2d2d 40%, #111 100%)",
    accentColor: "rgba(180,180,200,0.4)",
    borderColor: "rgba(180,180,200,0.35)",
    shadowColor: "rgba(0,0,0,0.4)",
    scoreColor: "#C8C8D8",
    fadeTo: "#111",
  },
  gold: {
    bgGradient: "linear-gradient(160deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%)",
    accentColor: "rgba(255,200,60,0.6)",
    borderColor: "rgba(255,200,60,0.5)",
    shadowColor: "rgba(255,180,30,0.3)",
    scoreColor: "#FFE566",
    fadeTo: "#16213e",
  },
  elite: {
    bgGradient: "linear-gradient(160deg, #2d1515 0%, #4a1010 40%, #1a0505 100%)",
    accentColor: "rgba(220,60,60,0.7)",
    borderColor: "rgba(220,60,60,0.6)",
    shadowColor: "rgba(255,60,60,0.35)",
    scoreColor: "#FF8080",
    fadeTo: "#1a0505",
  },
  legend: {
    bgGradient: "linear-gradient(160deg, #1a0d2e 0%, #2d1a4a 40%, #0d0d1a 100%)",
    accentColor: "rgba(180,100,255,0.6)",
    borderColor: "rgba(180,100,255,0.55)",
    shadowColor: "rgba(160,80,255,0.4)",
    scoreColor: "#D080FF",
    fadeTo: "#0d0d1a",
  },
}
