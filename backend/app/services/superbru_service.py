"""
superbru_service.py

Business logic for Superbru leaderboard caching, isolated from the endpoint layer.
"""

import json
from datetime import datetime, timedelta

from ..core.config import settings
from ..core.paths import SUPERBRU_LEADERBOARD_CACHE as CACHE_PATH

CACHE_TTL = timedelta(days=90)


def get_leaderboard(season: str) -> dict:
    """
    Return cached leaderboard points for a season.

    Finished seasons are cached permanently. The current season is
    refreshed after CACHE_TTL expires.

    Returns:
        dict with keys: global_top, global_top_250
    """
    cache = _load_cache()
    entry = cache.get(season)

    if entry:
        is_finished = season != settings.CURRENT_SEASON
        ts = datetime.fromisoformat(entry["timestamp"])
        if is_finished or datetime.now() - ts < CACHE_TTL:
            return {"global_top": entry["global_top"], "global_top_250": entry["global_top_250"]}

    # Cache missing or expired — scrape fresh data
    from .web_scraping.superbru.leaderboard_scraper import get_top_points
    global_top, global_top_250 = get_top_points()

    cache[season] = {
        "timestamp": datetime.now().isoformat(),
        "global_top": global_top,
        "global_top_250": global_top_250,
    }
    _save_cache(cache)

    return {"global_top": global_top, "global_top_250": global_top_250}


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)
