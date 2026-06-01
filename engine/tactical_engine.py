"""
Generic Tactical Analysis Engine
Evaluates players across 3 tactical phases and computes a Tactical Compatibility Score.

Supports any team tactical system: high-press, positional play, counter-attack, hybrid.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np
import pandas as pd


# ── Pitch constants (StatsBomb 120×80) ────────────────────────────────────────

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0

# Zone boundaries
DEFENSIVE_THIRD_X = 40.0
MIDDLE_THIRD_X = 80.0
# Half-spaces (StatsBomb coords): horizontal bands either side of centre
HALF_SPACE_X_LEFT_MIN = 18.0
HALF_SPACE_X_LEFT_MAX = 30.0
HALF_SPACE_X_RIGHT_MIN = 90.0
HALF_SPACE_X_RIGHT_MAX = 102.0
HALF_SPACE_Y_MIN = 20.0
HALF_SPACE_Y_MID = 35.0
HALF_SPACE_Y_MAX = 60.0
# Opponent box
BOX_X_MIN = 102.0
BOX_Y_MIN = 18.0
BOX_Y_MAX = 62.0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_col(df: pd.DataFrame, col: str, default=None) -> pd.Series:
    """Return df[col] if it exists, else a Series of `default`."""
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _expand_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand StatsBomb list-valued location columns into x/y float columns.
    StatsBomb flatten_attrs=True leaves location as [x, y] lists.
    Handles: location, pass_end_location, carry_end_location.
    """
    if df.empty:
        return df
    df = df.copy()

    def _parse(series: pd.Series, idx: int) -> pd.Series:
        return series.apply(
            lambda v: float(v[idx]) if isinstance(v, (list, tuple)) and len(v) > idx else np.nan
        )

    if "location" in df.columns and "location_x" not in df.columns:
        df["location_x"] = _parse(df["location"], 0)
        df["location_y"] = _parse(df["location"], 1)

    if "pass_end_location" in df.columns and "pass_end_location_x" not in df.columns:
        df["pass_end_location_x"] = _parse(df["pass_end_location"], 0)
        df["pass_end_location_y"] = _parse(df["pass_end_location"], 1)

    if "carry_end_location" in df.columns and "carry_end_location_x" not in df.columns:
        df["carry_end_location_x"] = _parse(df["carry_end_location"], 0)
        df["carry_end_location_y"] = _parse(df["carry_end_location"], 1)

    return df


def _player_events(events_df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    if events_df.empty or "player" not in events_df.columns:
        return pd.DataFrame()
    return events_df[events_df["player"] == player_name].copy()


def _event_minutes(events_df: pd.DataFrame) -> float:
    """Approximate total minutes in the events DataFrame."""
    if events_df.empty or "minute" not in events_df.columns:
        return 90.0
    return max(float(events_df["minute"].max()), 1.0)


# ── PhaseMapper ───────────────────────────────────────────────────────────────

# Position → generic zone mapping per formation family
_FORMATION_ZONES: dict[str, dict[str, str]] = {
    "4-3-3": {
        "Goalkeeper": "GK",
        "Right Back": "WB-R", "Left Back": "WB-L",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Right Midfield": "CM", "Left Midfield": "CM",
        "Center Midfield": "CM",
        "Defensive Midfield": "DM",
        "Left Center Midfield": "CM", "Right Center Midfield": "CM",
        "Attacking Midfield": "AM",
        "Right Wing": "FW-R", "Left Wing": "FW-L",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
    },
    "3-4-3": {
        "Goalkeeper": "GK",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Right Wing Back": "WB-R", "Left Wing Back": "WB-L",
        "Right Back": "WB-R", "Left Back": "WB-L",
        "Center Midfield": "CM",
        "Left Center Midfield": "CM", "Right Center Midfield": "CM",
        "Defensive Midfield": "DM",
        "Attacking Midfield": "AM",
        "Right Wing": "FW-R", "Left Wing": "FW-L",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
    },
    "3-2-5": {
        "Goalkeeper": "GK",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Defensive Midfield": "DM",
        "Center Midfield": "DM",
        "Right Wing": "FW-R", "Left Wing": "FW-L",
        "Right Midfield": "CM", "Left Midfield": "CM",
        "Attacking Midfield": "AM",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
        "Right Back": "FW-R", "Left Back": "FW-L",
    },
    "4-4-2": {
        "Goalkeeper": "GK",
        "Right Back": "WB-R", "Left Back": "WB-L",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Right Midfield": "WM-R", "Left Midfield": "WM-L",
        "Center Midfield": "CM",
        "Left Center Midfield": "CM", "Right Center Midfield": "CM",
        "Defensive Midfield": "DM",
        "Attacking Midfield": "AM",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
    },
    "4-2-3-1": {
        "Goalkeeper": "GK",
        "Right Back": "WB-R", "Left Back": "WB-L",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Defensive Midfield": "DM",
        "Center Midfield": "CM",
        "Right Midfield": "WM-R", "Left Midfield": "WM-L",
        "Attacking Midfield": "AM",
        "Right Wing": "FW-R", "Left Wing": "FW-L",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
    },
    "5-3-2": {
        "Goalkeeper": "GK",
        "Right Back": "WB-R", "Left Back": "WB-L",
        "Right Wing Back": "WB-R", "Left Wing Back": "WB-L",
        "Right Center Back": "CB", "Left Center Back": "CB",
        "Center Back": "CB",
        "Center Midfield": "CM",
        "Left Center Midfield": "CM", "Right Center Midfield": "CM",
        "Defensive Midfield": "DM",
        "Center Forward": "ST",
        "Secondary Striker": "ST",
    },
}

# Canonical fallback: position string → zone
_GENERIC_ZONE: dict[str, str] = {
    "Goalkeeper": "GK",
    "Right Back": "WB-R", "Left Back": "WB-L",
    "Right Wing Back": "WB-R", "Left Wing Back": "WB-L",
    "Center Back": "CB", "Right Center Back": "CB", "Left Center Back": "CB",
    "Defensive Midfield": "DM",
    "Center Midfield": "CM", "Left Center Midfield": "CM", "Right Center Midfield": "CM",
    "Right Midfield": "WM-R", "Left Midfield": "WM-L",
    "Attacking Midfield": "AM",
    "Right Wing": "FW-R", "Left Wing": "FW-L",
    "Center Forward": "ST", "Secondary Striker": "ST",
}

# All possible zones for coverage scoring
_ALL_ZONES = {"GK", "CB", "WB-L", "WB-R", "DM", "CM", "WM-L", "WM-R", "AM", "FW-L", "FW-R", "ST"}


class PhaseMapper:
    """
    Maps player positions to tactical zones for three configurable phases.

    Parameters
    ----------
    phase_config : dict with keys 'buildup', 'progression', 'finish'
                   Values are formation strings, e.g. '4-3-3'.
    """

    def __init__(self, phase_config: dict):
        self.phase_config = {
            "buildup": phase_config.get("buildup", "4-3-3"),
            "progression": phase_config.get("progression", "3-4-3"),
            "finish": phase_config.get("finish", "3-2-5"),
        }

    def _get_formation_map(self, formation: str) -> dict[str, str]:
        """Return position→zone dict for the closest matching formation."""
        # Try exact match first
        if formation in _FORMATION_ZONES:
            return _FORMATION_ZONES[formation]
        # Try prefix match (e.g. "4-3-3" matches "4-3-3 (attack)")
        for key in _FORMATION_ZONES:
            if formation.startswith(key) or key.startswith(formation):
                return _FORMATION_ZONES[key]
        return _GENERIC_ZONE

    def map_position(self, player_position: str, phase: str) -> str:
        """
        Return the tactical zone for a given player position in the given phase.

        Parameters
        ----------
        player_position : StatsBomb position string, e.g. 'Right Back'
        phase : 'buildup' | 'progression' | 'finish'
        """
        formation = self.phase_config.get(phase, "4-3-3")
        mapping = self._get_formation_map(formation)
        zone = mapping.get(player_position)
        if zone:
            return zone
        # Try generic fallback
        return _GENERIC_ZONE.get(player_position, "CM")

    def versatility_score(self, player_positions: list[str]) -> float:
        """
        Return 0–10 versatility score based on how many distinct zones/phases the player covers.

        Bonus for covering multiple phases and different zone types.
        """
        if not player_positions:
            return 0.0

        covered_zones: set[str] = set()
        per_phase_zones: dict[str, set[str]] = {p: set() for p in self.phase_config}

        for pos in player_positions:
            for phase in self.phase_config:
                zone = self.map_position(pos, phase)
                covered_zones.add(zone)
                per_phase_zones[phase].add(zone)

        # Base: fraction of all zones covered
        zone_fraction = len(covered_zones) / len(_ALL_ZONES)
        base_score = zone_fraction * 6.0  # max 6 from zone coverage

        # Phase bonus: +1.5 per phase with more than 1 unique zone
        phase_bonus = sum(
            1.5 for zones in per_phase_zones.values() if len(zones) > 1
        )

        # Versatility bonus if player covers both attacking and defensive zones
        attacking = {"FW-L", "FW-R", "ST", "AM"}
        defensive = {"GK", "CB", "WB-L", "WB-R"}
        cross_bonus = 0.0
        if covered_zones & attacking and covered_zones & defensive:
            cross_bonus = 2.0
        elif covered_zones & attacking and covered_zones & {"DM", "CM", "WM-L", "WM-R"}:
            cross_bonus = 1.0
        elif covered_zones & defensive and covered_zones & {"DM", "CM", "WM-L", "WM-R"}:
            cross_bonus = 1.0

        score = base_score + phase_bonus + cross_bonus
        return round(min(score, 10.0), 2)


# ── PressingEngine ────────────────────────────────────────────────────────────

class PressingEngine:
    """
    Computes pressing-related KPIs from a StatsBomb events DataFrame.

    Parameters
    ----------
    events_df : full match events (all players)
    """

    def __init__(self, events_df: pd.DataFrame):
        self.events_df = events_df.copy() if not events_df.empty else pd.DataFrame()
        self._total_minutes = _event_minutes(events_df)

    def pressing_frequency(self, player_name: str) -> float:
        """
        Pressure events per 90 minutes for the player.
        """
        if self.events_df.empty:
            return 0.0
        pe = _player_events(self.events_df, player_name)
        if pe.empty or "type" not in pe.columns:
            return 0.0
        n_pressures = int((pe["type"] == "Pressure").sum())
        per_90 = n_pressures / self._total_minutes * 90.0
        return round(per_90, 2)

    def counterpressing_efficiency(self, player_name: str, window_seconds: int = 5) -> float:
        """
        Fraction of possession-loss events where the player responded with a pressure
        within `window_seconds`.

        Possession losses are: Miscontrol, Dispossessed, incomplete Pass (pass_outcome not NaN).
        Returns a value in [0, 1].
        """
        if self.events_df.empty:
            return 0.0

        df = self.events_df
        if "type" not in df.columns:
            return 0.0

        # Identify possession-loss events for *all* teammates (we track their losses, player responds)
        # More useful: track the player's own pressing after any team possession loss
        # We use: any 'Miscontrol' or 'Dispossessed' by any player on same team
        player_events = _player_events(df, player_name)
        if player_events.empty:
            return 0.0

        # Get player's team
        if "team" not in df.columns:
            return 0.0
        player_team_series = player_events["team"].dropna()
        if player_team_series.empty:
            return 0.0
        player_team = player_team_series.iloc[0]

        team_df = df[df["team"] == player_team].copy()

        # Possession losses: Miscontrol or Dispossessed by team
        loss_types = {"Miscontrol", "Dispossessed"}
        # Also incomplete passes
        losses = team_df[team_df["type"].isin(loss_types)].copy()

        # Add incomplete passes as possession losses
        if "pass_outcome" in df.columns:
            inc_passes = team_df[
                (team_df["type"] == "Pass") &
                (team_df["pass_outcome"].notna())
            ].copy()
            losses = pd.concat([losses, inc_passes], ignore_index=True)

        if losses.empty:
            return 0.0

        # Build timestamp column (minute * 60 + second)
        def _ts(frame: pd.DataFrame) -> pd.Series:
            minutes = frame["minute"].fillna(0) if "minute" in frame.columns else pd.Series(0, index=frame.index)
            seconds = frame["second"].fillna(0) if "second" in frame.columns else pd.Series(0, index=frame.index)
            return minutes * 60.0 + seconds

        losses = losses.copy()
        losses["_ts"] = _ts(losses)

        pressures = player_events[player_events["type"] == "Pressure"].copy()
        if pressures.empty:
            return 0.0
        pressures["_ts"] = _ts(pressures)

        pressure_times = pressures["_ts"].values
        responded = 0

        for loss_ts in losses["_ts"].values:
            # Check if any pressure within window
            diffs = pressure_times - loss_ts
            if np.any((diffs >= 0) & (diffs <= window_seconds)):
                responded += 1

        efficiency = responded / len(losses)
        return round(min(efficiency, 1.0), 4)

    def distance_covered_estimate(self, player_name: str) -> float:
        """
        Proxy estimate of distance covered (km) using carry lengths + pressure event counts.

        Carries contribute physical distance; each pressure event adds ~15m sprint estimate.
        Result is normalized to a plausible match range (5–14 km).
        """
        if self.events_df.empty:
            return 0.0

        pe = _player_events(self.events_df, player_name)
        if pe.empty:
            return 0.0

        carry_distance = 0.0
        if "type" in pe.columns:
            carries = pe[pe["type"] == "Carry"]
            if not carries.empty:
                # StatsBomb carry_length in metres
                if "carry_length" in carries.columns:
                    carry_distance = float(carries["carry_length"].fillna(0).sum())
                else:
                    # Estimate from location → end_location
                    loc_x = _safe_col(carries, "location_x", 0).fillna(0)
                    loc_y = _safe_col(carries, "location_y", 0).fillna(0)
                    end_x = _safe_col(carries, "carry_end_location_x", 0).fillna(0)
                    end_y = _safe_col(carries, "carry_end_location_y", 0).fillna(0)
                    dists = np.sqrt((end_x - loc_x) ** 2 + (end_y - loc_y) ** 2)
                    carry_distance = float(dists.sum())

        # Each pressure adds ~15m sprint
        n_pressures = int((pe["type"] == "Pressure").sum()) if "type" in pe.columns else 0
        pressure_distance = n_pressures * 15.0  # metres

        # Base jog/walk estimate: ~7000m for an outfield player
        base_distance = 7000.0

        total_m = base_distance + carry_distance + pressure_distance
        total_km = total_m / 1000.0

        # Clamp to realistic range
        return round(max(4.0, min(total_km, 14.0)), 2)


# ── AnimationModules ──────────────────────────────────────────────────────────

class FalseNineAnalyzer:
    """
    Detects false-nine / deep-dropping forward behaviors in event data.
    """

    @staticmethod
    def axial_drops(events_df: pd.DataFrame, player_name: str) -> int:
        """
        Count events where the player (forward) receives the ball in the midfield zone.
        Midfield zone definition: x in [40, 80] (middle third) on a 120×80 pitch.

        Uses 'Ball Receipt*' event type; falls back to any event in zone.
        """
        if events_df.empty:
            return 0

        pe = _player_events(events_df, player_name)
        if pe.empty:
            return 0

        # Use Ball Receipt events or all events with location
        receipt_types = {"Ball Receipt*", "Pass", "Carry"}
        if "type" in pe.columns:
            pe = pe[pe["type"].isin(receipt_types)]

        loc_x = _safe_col(pe, "location_x", None)
        loc_y = _safe_col(pe, "location_y", None)

        if loc_x is None or loc_x.isna().all():
            # Try to parse location tuple column
            if "location" in pe.columns:
                def _extract_x(loc):
                    try:
                        if isinstance(loc, (list, tuple)):
                            return float(loc[0])
                        return float(str(loc).strip("[]()").split(",")[0])
                    except Exception:
                        return None
                loc_x = pe["location"].apply(_extract_x)
            else:
                return 0

        # Midfield zone: x between 40 and 80
        mask = (loc_x >= DEFENSIVE_THIRD_X) & (loc_x <= MIDDLE_THIRD_X)
        return int(mask.sum())

    @staticmethod
    def space_creation_index(events_df: pd.DataFrame, player_name: str) -> float:
        """
        When the player drops deep (axial drop), count teammate actions in the final third.
        Returns a float index: mean teammate final-third actions per player drop.
        """
        if events_df.empty:
            return 0.0

        pe = _player_events(events_df, player_name)
        if pe.empty:
            return 0.0

        if "team" not in events_df.columns:
            return 0.0

        player_team = pe["team"].dropna().iloc[0] if not pe["team"].dropna().empty else None
        if not player_team:
            return 0.0

        # Player's midfield receipts with timestamps
        receipt_types = {"Ball Receipt*", "Pass", "Carry"}
        if "type" in pe.columns:
            drops = pe[pe["type"].isin(receipt_types)].copy()
        else:
            drops = pe.copy()

        loc_x = _safe_col(drops, "location_x", None)
        if loc_x is None or loc_x.isna().all():
            return 0.0

        drops = drops[loc_x.between(DEFENSIVE_THIRD_X, MIDDLE_THIRD_X)]
        if drops.empty:
            return 0.0

        # Teammate events
        teammates = events_df[
            (events_df["team"] == player_team) &
            (events_df["player"] != player_name)
        ].copy()

        if teammates.empty or "minute" not in teammates.columns:
            return float(len(drops))  # return raw count as proxy

        final_third_types = {"Carry", "Pass", "Shot", "Dribble", "Ball Receipt*"}
        if "type" in teammates.columns:
            teammates = teammates[teammates["type"].isin(final_third_types)]

        t_loc_x = _safe_col(teammates, "location_x", None)
        if t_loc_x is not None and not t_loc_x.isna().all():
            teammates = teammates[t_loc_x >= MIDDLE_THIRD_X]

        if teammates.empty or "minute" not in drops.columns:
            return 0.0

        # For each drop, count teammate final-third actions within next 10 seconds
        def _ts_sec(df: pd.DataFrame) -> pd.Series:
            m = df["minute"].fillna(0) if "minute" in df.columns else pd.Series(0, index=df.index)
            s = df["second"].fillna(0) if "second" in df.columns else pd.Series(0, index=df.index)
            return m * 60.0 + s

        drops["_ts"] = _ts_sec(drops)
        teammates["_ts"] = _ts_sec(teammates)

        total_actions = 0
        t_times = teammates["_ts"].values
        for drop_ts in drops["_ts"].values:
            window = (t_times >= drop_ts) & (t_times <= drop_ts + 10.0)
            total_actions += int(window.sum())

        return round(total_actions / max(len(drops), 1), 2)


class ProjectionAnalyzer:
    """
    Detects forward runs and projections into dangerous areas.
    """

    @staticmethod
    def half_space_runs(events_df: pd.DataFrame, player_name: str) -> int:
        """
        Count carries and received passes in the half-spaces.
        Half-spaces on a 120×80 pitch:
        - Left: x ∈ [18, 30], y ∈ [20, 45]  OR  x ∈ [90, 102], y ∈ [20, 45]
        - Right: x ∈ [18, 30], y ∈ [35, 60]  OR  x ∈ [90, 102], y ∈ [35, 60]
        """
        if events_df.empty:
            return 0

        pe = _player_events(events_df, player_name)
        if pe.empty:
            return 0

        half_space_event_types = {"Carry", "Ball Receipt*", "Pass", "Shot", "Dribble"}
        if "type" in pe.columns:
            pe = pe[pe["type"].isin(half_space_event_types)]

        loc_x = _safe_col(pe, "location_x", None)
        loc_y = _safe_col(pe, "location_y", None)

        if loc_x is None or loc_x.isna().all():
            return 0

        loc_x = loc_x.fillna(-1)
        loc_y = loc_y.fillna(-1) if loc_y is not None else pd.Series(-1, index=pe.index)

        # Half-space condition
        in_x_left = (loc_x >= HALF_SPACE_X_LEFT_MIN) & (loc_x <= HALF_SPACE_X_LEFT_MAX)
        in_x_right = (loc_x >= HALF_SPACE_X_RIGHT_MIN) & (loc_x <= HALF_SPACE_X_RIGHT_MAX)
        in_y_lower = (loc_y >= HALF_SPACE_Y_MIN) & (loc_y <= HALF_SPACE_Y_MID)
        in_y_upper = (loc_y >= HALF_SPACE_Y_MID) & (loc_y <= HALF_SPACE_Y_MAX)

        in_half_space = (in_x_left | in_x_right) & (in_y_lower | in_y_upper)
        return int(in_half_space.sum())

    @staticmethod
    def second_line_projections(events_df: pd.DataFrame, player_name: str) -> int:
        """
        Count actions in opponent's penalty box by a player who is primarily a
        midfielder or defender (second-line runner appearing in box).

        Uses box definition: x > 102, y ∈ [18, 62].
        """
        if events_df.empty:
            return 0

        pe = _player_events(events_df, player_name)
        if pe.empty:
            return 0

        box_types = {"Shot", "Carry", "Pass", "Ball Receipt*", "Dribble", "Duel"}
        if "type" in pe.columns:
            pe = pe[pe["type"].isin(box_types)]

        loc_x = _safe_col(pe, "location_x", None)
        loc_y = _safe_col(pe, "location_y", None)

        if loc_x is None or loc_x.isna().all():
            return 0

        loc_x = loc_x.fillna(-1)
        loc_y = loc_y.fillna(-1) if loc_y is not None else pd.Series(-1, index=pe.index)

        in_box = (loc_x >= BOX_X_MIN) & (loc_y >= BOX_Y_MIN) & (loc_y <= BOX_Y_MAX)
        return int(in_box.sum())


class GoalkeeperAnalyzer:
    """
    Goalkeeper-specific metrics for modern ball-playing sweeper-keepers.
    """

    @staticmethod
    def pass_under_pressure_accuracy(events_df: pd.DataFrame, gk_name: str) -> float:
        """
        Percentage of passes completed when a pressure event from the opponent
        occurred within 2 seconds before the pass.

        Returns a float in [0, 1].
        """
        if events_df.empty:
            return 0.0

        pe = _player_events(events_df, gk_name)
        if pe.empty:
            return 0.0

        if "type" not in pe.columns:
            return 0.0

        gk_passes = pe[pe["type"] == "Pass"].copy()
        if gk_passes.empty:
            return 0.0

        # Get opponent pressures
        if "team" not in events_df.columns:
            return 0.0
        gk_team = pe["team"].dropna().iloc[0] if not pe["team"].dropna().empty else None
        if not gk_team:
            return 0.0

        opponent_pressures = events_df[
            (events_df["team"] != gk_team) &
            (events_df["type"] == "Pressure")
        ].copy()

        def _ts(df: pd.DataFrame) -> pd.Series:
            m = df["minute"].fillna(0) if "minute" in df.columns else pd.Series(0, index=df.index)
            s = df["second"].fillna(0) if "second" in df.columns else pd.Series(0, index=df.index)
            return m * 60.0 + s

        if "minute" not in gk_passes.columns:
            # Can't compute timing — fall back to raw completion rate
            if "pass_outcome" in gk_passes.columns:
                completed = gk_passes["pass_outcome"].isna().sum()
                return round(completed / len(gk_passes), 4)
            return 0.0

        gk_passes["_ts"] = _ts(gk_passes)

        if opponent_pressures.empty:
            # No pressure data; return overall completion
            if "pass_outcome" in gk_passes.columns:
                completed = gk_passes["pass_outcome"].isna().sum()
                return round(completed / len(gk_passes), 4)
            return 1.0

        opponent_pressures["_ts"] = _ts(opponent_pressures)
        opp_times = opponent_pressures["_ts"].values

        pressured_pass_mask = []
        for pass_ts in gk_passes["_ts"].values:
            was_pressured = np.any(
                (opp_times >= pass_ts - 2.0) & (opp_times <= pass_ts + 0.5)
            )
            pressured_pass_mask.append(was_pressured)

        pressured_passes = gk_passes[pressured_pass_mask]
        if pressured_passes.empty:
            return 1.0  # no pressured passes recorded → 100% (vacuously true)

        if "pass_outcome" in pressured_passes.columns:
            completed = pressured_passes["pass_outcome"].isna().sum()
        else:
            completed = len(pressured_passes)  # assume all completed

        return round(completed / len(pressured_passes), 4)

    @staticmethod
    def build_up_participation(events_df: pd.DataFrame, gk_name: str) -> float:
        """
        Passes per 90 minutes from own half (x ≤ 60), excluding goal kicks.
        """
        if events_df.empty:
            return 0.0

        pe = _player_events(events_df, gk_name)
        if pe.empty:
            return 0.0

        if "type" not in pe.columns:
            return 0.0

        passes = pe[pe["type"] == "Pass"].copy()
        if passes.empty:
            return 0.0

        # Exclude goal kicks
        if "pass_type" in passes.columns:
            passes = passes[passes["pass_type"] != "Goal Kick"]

        # Own half: x ≤ 60
        loc_x = _safe_col(passes, "location_x", 0).fillna(0)
        own_half = passes[loc_x <= 60.0]

        total_minutes = _event_minutes(events_df)
        per_90 = len(own_half) / total_minutes * 90.0
        return round(per_90, 2)


# ── MatchReport ───────────────────────────────────────────────────────────────

@dataclass
class MatchReport:
    player_name: str
    match_id: int
    possession_share: float
    pressing_triggers: int
    vertical_passes_ratio: float
    counterpressing_efficiency: float
    versatility_score: float
    false_nine_drops: int
    half_space_runs: int
    distance_estimate_km: float
    tactical_compatibility_score: float
    tactical_feedback: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# ── Tactical feedback generation ──────────────────────────────────────────────

def _generate_feedback(
    report_data: dict,
    team_style: str,
    player_position: str,
) -> list[str]:
    """
    Generate 3–5 actionable French-language tactical observations.
    """
    feedback = []
    score = report_data["tactical_compatibility_score"]
    pressing = report_data["pressing_triggers"]
    vpr = report_data["vertical_passes_ratio"]
    cp_eff = report_data["counterpressing_efficiency"]
    versatility = report_data["versatility_score"]
    hs_runs = report_data["half_space_runs"]
    drops = report_data["false_nine_drops"]
    distance = report_data["distance_estimate_km"]
    possession = report_data["possession_share"]

    # ── Style-specific observations ──────────────────────────────────────────
    if team_style == "high-press":
        if pressing >= 15:
            feedback.append(
                f"Pressing très actif ({pressing:.0f} actions/90) : ce joueur correspond bien "
                "au profil d'un pressing haut avec déclenchement fréquent."
            )
        elif pressing >= 8:
            feedback.append(
                f"Pressing modéré ({pressing:.0f} actions/90) : le joueur peut s'améliorer dans "
                "le déclenchement du pressing pour correspondre à un bloc haut."
            )
        else:
            feedback.append(
                f"Pressing insuffisant ({pressing:.0f} actions/90) pour un système de pressing "
                "intense — nécessite un travail spécifique sur les déclencheurs de pressing."
            )

        if cp_eff >= 0.5:
            feedback.append(
                f"Contre-pressing efficace ({cp_eff*100:.0f}% des pertes récupérées) : "
                "excellente réactivité après la perte de balle."
            )
        else:
            feedback.append(
                f"Contre-pressing à améliorer ({cp_eff*100:.0f}%) : "
                "doit réagir plus vite après les pertes de possession de l'équipe."
            )

    elif team_style == "positional":
        if vpr >= 0.35:
            feedback.append(
                f"Bon volume de passes verticales/progressives ({vpr*100:.0f}%) : "
                "favorise la progression dans les lignes, essentiel au jeu de position."
            )
        else:
            feedback.append(
                f"Passes trop latérales ({vpr*100:.0f}% de passes verticales) : "
                "doit augmenter le jeu entre les lignes pour fluidifier le jeu positionnel."
            )

        if possession >= 0.55:
            feedback.append(
                "Participation forte à la conservation du ballon — "
                "s'inscrit bien dans un jeu de possession structuré."
            )

        if versatility >= 7.0:
            feedback.append(
                f"Excellente polyvalence tactique (score {versatility:.1f}/10) : "
                "capable d'occuper plusieurs zones selon la phase de jeu, idéal en jeu positionnel."
            )
        elif versatility < 4.0:
            feedback.append(
                f"Polyvalence limitée ({versatility:.1f}/10) : dans un bloc positionnel, "
                "il est conseillé de développer la capacité à évoluer dans plusieurs zones."
            )

    elif team_style == "counter":
        if distance >= 10.0:
            feedback.append(
                f"Distance parcourue estimée élevée ({distance:.1f} km) : "
                "profil athlétique adapté aux transitions rapides en contre-attaque."
            )
        if vpr >= 0.40:
            feedback.append(
                f"Passes verticales dominantes ({vpr*100:.0f}%) : "
                "accélération du jeu vers l'avant, parfait pour le jeu en transition."
            )
        if hs_runs >= 5:
            feedback.append(
                f"Fréquentes incursions dans les demi-espaces ({hs_runs} actions) : "
                "crée de la profondeur et décale la défense adverse en contre."
            )

    elif team_style == "hybrid":
        feedback.append(
            f"Score de compatibilité global : {score:.0f}/100 — "
            "profil polyvalent, adaptable selon le contexte de match."
        )

    # ── Generic observations (always included if relevant) ────────────────────
    if hs_runs >= 8 and team_style != "counter":
        feedback.append(
            f"Forte présence dans les demi-espaces ({hs_runs} actions) : "
            "génère des déséquilibres structuraux dans la défense adverse."
        )

    if drops >= 5:
        feedback.append(
            f"Décrochages axiaux fréquents ({drops} occurrences) : "
            "interprétation du rôle de faux-neuf ou milieu projeté — crée du surnombre au milieu."
        )

    if distance < 7.0 and team_style in {"high-press", "counter"}:
        feedback.append(
            f"Distance estimée faible ({distance:.1f} km) : "
            "le volume physique semble insuffisant pour un système à haute intensité."
        )

    if score >= 80:
        feedback.append(
            "Compatibilité tactique excellente : le joueur s'inscrit parfaitement "
            "dans ce système de jeu — à valoriser dans les matchs à enjeu."
        )
    elif score < 40:
        feedback.append(
            "Compatibilité tactique faible : une adaptation tactique ou un changement "
            "de poste est recommandé pour mieux correspondre au style de jeu cible."
        )

    # Deduplicate and limit
    seen = set()
    unique_feedback = []
    for f in feedback:
        if f not in seen:
            seen.add(f)
            unique_feedback.append(f)

    return unique_feedback[:5]


# ── compute_tactical_score — main entry point ─────────────────────────────────

def compute_tactical_score(
    events_df: pd.DataFrame,
    player_name: str,
    player_position: str,
    team_style: str = "positional",
    phase_config: dict = None,
    match_id: int = 0,
) -> MatchReport:
    """
    Compute the Tactical Compatibility Score (0–100) for a player and return a MatchReport.

    Parameters
    ----------
    events_df     : Full match events DataFrame (all players, StatsBomb format).
    player_name   : Player display name (must match 'player' column in events_df).
    player_position: StatsBomb position string, e.g. 'Right Back'.
    team_style    : 'positional' | 'high-press' | 'counter' | 'hybrid'
    phase_config  : dict with keys 'buildup', 'progression', 'finish' → formation strings.
                    Defaults to {'buildup':'4-3-3','progression':'3-4-3','finish':'3-2-5'}.
    match_id      : Match identifier (stored in report; optional).

    Returns
    -------
    MatchReport instance.
    """
    if phase_config is None:
        phase_config = {"buildup": "4-3-3", "progression": "3-4-3", "finish": "3-2-5"}

    # Expand list-valued location columns so all engines can use location_x / location_y
    events_df = _expand_locations(events_df)

    # ── Sub-engines ────────────────────────────────────────────────────────────
    phase_mapper = PhaseMapper(phase_config)
    pressing_engine = PressingEngine(events_df)
    false_nine = FalseNineAnalyzer()
    projector = ProjectionAnalyzer()

    # ── Pressing metrics ───────────────────────────────────────────────────────
    pressing_freq = pressing_engine.pressing_frequency(player_name)          # per 90
    cp_eff = pressing_engine.counterpressing_efficiency(player_name)          # 0–1
    distance_km = pressing_engine.distance_covered_estimate(player_name)     # km

    # ── Versatility ────────────────────────────────────────────────────────────
    # Collect all positions this player appears in during the match
    player_ev = _player_events(events_df, player_name)
    player_positions_in_match: list[str] = []
    if not player_ev.empty and "position" in player_ev.columns:
        player_positions_in_match = player_ev["position"].dropna().unique().tolist()
    if not player_positions_in_match:
        player_positions_in_match = [player_position]
    versatility = phase_mapper.versatility_score(player_positions_in_match)

    # ── Pass metrics ──────────────────────────────────────────────────────────
    # vertical / progressive passes ratio
    vertical_passes_ratio = 0.0
    pressing_triggers_raw = 0
    possession_share = 0.0

    if not player_ev.empty and "type" in player_ev.columns:
        passes = player_ev[player_ev["type"] == "Pass"]
        n_passes = len(passes)

        if n_passes > 0:
            # Progressive pass: end_x > start_x + 10 (StatsBomb definition proxy)
            loc_x = _safe_col(passes, "location_x", 0).fillna(0)
            end_x = _safe_col(passes, "pass_end_location_x", 0).fillna(0)
            progressive_mask = (end_x - loc_x) >= 10.0
            n_progressive = int(progressive_mask.sum())
            vertical_passes_ratio = round(n_progressive / n_passes, 4)

        # Pressing triggers = Pressure events
        pressing_triggers_raw = int((player_ev["type"] == "Pressure").sum())

        # Possession share: fraction of match events belonging to player's team
        if "team" in events_df.columns and "team" in player_ev.columns:
            team_name = player_ev["team"].dropna().iloc[0] if not player_ev["team"].dropna().empty else None
            if team_name:
                team_events = len(events_df[events_df["team"] == team_name])
                total_events = len(events_df)
                possession_share = round(team_events / max(total_events, 1), 4)

    # ── FalseNine / Half-space ─────────────────────────────────────────────────
    fn_drops = false_nine.axial_drops(events_df, player_name)
    hs_runs = projector.half_space_runs(events_df, player_name)

    # ── Scoring weights ───────────────────────────────────────────────────────
    # Normalise each component to [0, 1] before weighting

    def _norm(value: float, lo: float, hi: float) -> float:
        if hi <= lo:
            return 0.0
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))

    # Normalisation ranges (domain knowledge)
    n_pressing = _norm(pressing_freq, 0, 30)        # 0–30 per 90
    n_cp_eff = cp_eff                                 # already 0–1
    n_distance = _norm(distance_km, 4, 14)           # 4–14 km
    n_vpr = _norm(vertical_passes_ratio, 0, 0.7)    # 0–70%
    n_versatility = _norm(versatility, 0, 10)        # 0–10
    n_hs = _norm(hs_runs, 0, 20)                     # 0–20 events

    style_weights = {
        "positional": {
            "possession": 0.20,
            "vertical_passes": 0.25,
            "versatility": 0.20,
            "half_space": 0.15,
            "pressing": 0.20,
        },
        "high-press": {
            "pressing": 0.35,
            "counterpressing": 0.25,
            "distance": 0.20,
            "vertical_passes": 0.20,
        },
        "counter": {
            "vertical_passes": 0.35,
            "distance": 0.25,
            "half_space": 0.20,
            "pressing": 0.20,
        },
        "hybrid": {
            "pressing": 0.175,
            "counterpressing": 0.175,
            "distance": 0.125,
            "vertical_passes": 0.175,
            "versatility": 0.175,
            "half_space": 0.175,
        },
    }

    weights = style_weights.get(team_style, style_weights["hybrid"])

    # Map component names to normalised values
    component_map = {
        "possession": _norm(possession_share, 0.3, 0.7),
        "vertical_passes": n_vpr,
        "versatility": n_versatility,
        "half_space": n_hs,
        "pressing": n_pressing,
        "counterpressing": n_cp_eff,
        "distance": n_distance,
    }

    raw_score = sum(component_map.get(comp, 0.0) * w for comp, w in weights.items())
    tactical_score = round(raw_score * 100.0, 1)

    # ── Build report dict for feedback ────────────────────────────────────────
    report_data = {
        "tactical_compatibility_score": tactical_score,
        "pressing_triggers": pressing_triggers_raw,
        "vertical_passes_ratio": vertical_passes_ratio,
        "counterpressing_efficiency": cp_eff,
        "versatility_score": versatility,
        "false_nine_drops": fn_drops,
        "half_space_runs": hs_runs,
        "distance_estimate_km": distance_km,
        "possession_share": possession_share,
    }

    feedback = _generate_feedback(report_data, team_style, player_position)

    return MatchReport(
        player_name=player_name,
        match_id=match_id,
        possession_share=possession_share,
        pressing_triggers=pressing_triggers_raw,
        vertical_passes_ratio=vertical_passes_ratio,
        counterpressing_efficiency=cp_eff,
        versatility_score=versatility,
        false_nine_drops=fn_drops,
        half_space_runs=hs_runs,
        distance_estimate_km=distance_km,
        tactical_compatibility_score=tactical_score,
        tactical_feedback=feedback,
    )
