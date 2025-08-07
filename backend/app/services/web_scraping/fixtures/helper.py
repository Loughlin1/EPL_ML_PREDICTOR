"""
fixtures/helper.py

    Functions for scraping fixtures data.
"""

import regex


def generate_seasons(start_year: int, end_year: int):
    """
    Generate a list of seasons from start_year to end_year.
    Args:
        start_year: int (e.g. 2024)
        end_year: int (e.g. 2025)
    Returns:
        list of seasons (e.g. ["2024-2025", "2025-2026"])
    """
    seasons = []
    for year in range(start_year, end_year + 1):
        season_start = str(year)
        season_end = str(year + 1)
        season = f"{season_start}-{season_end}"
        seasons.append(season)
    return seasons
