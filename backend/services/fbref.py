"""
FBref data service using soccerdata.
Handles network failures gracefully and caches results with lru_cache.
"""

from __future__ import annotations

import logging
from functools import lru_cache

import pandas as pd

logger = logging.getLogger(__name__)

# Supported leagues in soccerdata FBref format
SUPPORTED_LEAGUES = {
    "Premier League (ENG)": "ENG-Premier League",
    "La Liga (ESP)": "ESP-La Liga",
    "Bundesliga (GER)": "GER-Bundesliga",
    "Serie A (ITA)": "ITA-Serie A",
    "Ligue 1 (FRA)": "FRA-Ligue 1",
    "Champions League": "INT-Champions League",
    "MLS (USA)": "USA-Major League Soccer",
}

SUPPORTED_SEASONS = ["2024-2025", "2023-2024", "2022-2023", "2021-2022"]


def _get_fbref_client(league: str, season: str):
    """Instantiate a soccerdata FBref scraper, or return None on failure."""
    try:
        import soccerdata as sd  # type: ignore
        return sd.FBref(leagues=league, seasons=season)
    except ImportError:
        logger.warning("soccerdata n'est pas installé. Installez-le avec `pip install soccerdata`.")
        return None
    except Exception as e:
        logger.warning("Impossible d'initialiser FBref : %s", e)
        return None


@lru_cache(maxsize=16)
def get_player_stats(league: str, season: str) -> pd.DataFrame:
    """
    Load player stats from FBref for a given league / season.
    Returns an empty DataFrame on failure.

    Parameters
    ----------
    league : soccerdata league key, e.g. 'ENG-Premier League'
    season : e.g. '2023-2024'
    """
    fbref = _get_fbref_client(league, season)
    if fbref is None:
        return pd.DataFrame()
    try:
        stats = fbref.read_player_season_stats(stat_type="standard")
        if stats is None:
            return pd.DataFrame()
        stats = stats.reset_index()
        return stats
    except Exception as e:
        logger.warning("Erreur lors du chargement des stats joueurs FBref : %s", e)
        return pd.DataFrame()


@lru_cache(maxsize=16)
def get_team_stats(league: str, season: str) -> pd.DataFrame:
    """
    Load team stats from FBref for a given league / season.
    Returns an empty DataFrame on failure.
    """
    fbref = _get_fbref_client(league, season)
    if fbref is None:
        return pd.DataFrame()
    try:
        stats = fbref.read_team_season_stats(stat_type="standard")
        if stats is None:
            return pd.DataFrame()
        stats = stats.reset_index()
        return stats
    except Exception as e:
        logger.warning("Erreur lors du chargement des stats équipes FBref : %s", e)
        return pd.DataFrame()


@lru_cache(maxsize=16)
def get_shooting_stats(league: str, season: str) -> pd.DataFrame:
    """Load shooting stats (xG, shots) from FBref."""
    fbref = _get_fbref_client(league, season)
    if fbref is None:
        return pd.DataFrame()
    try:
        stats = fbref.read_player_season_stats(stat_type="shooting")
        if stats is None:
            return pd.DataFrame()
        return stats.reset_index()
    except Exception as e:
        logger.warning("Erreur shooting stats FBref : %s", e)
        return pd.DataFrame()


@lru_cache(maxsize=16)
def get_passing_stats(league: str, season: str) -> pd.DataFrame:
    """Load passing stats from FBref."""
    fbref = _get_fbref_client(league, season)
    if fbref is None:
        return pd.DataFrame()
    try:
        stats = fbref.read_player_season_stats(stat_type="passing")
        if stats is None:
            return pd.DataFrame()
        return stats.reset_index()
    except Exception as e:
        logger.warning("Erreur passing stats FBref : %s", e)
        return pd.DataFrame()


def get_league_label(league_key: str) -> str:
    """Reverse-lookup human label from soccerdata league key."""
    for label, key in SUPPORTED_LEAGUES.items():
        if key == league_key:
            return label
    return league_key
