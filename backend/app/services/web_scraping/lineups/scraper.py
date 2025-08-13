from ....db.updaters.lineups import upsert_lineups
from ....db.queries import get_seasons_fixtures, get_lineups, get_match_id
from .prematch_lineups_scraper import get_match_report
from .historical_lineups_scraper import scrape_match_report, retrieve_fixtures_table
from datetime import datetime
from ....core.config import settings

import traceback
import logging
import sys
import time
import random


def scrape_lineups(season: str, week: int = None):
    """
    Function to scrape the lineups for a given season and week.
    """
    matches = get_seasons_fixtures(season=season, week=week)

    if season == settings.CURRENT_SEASON:
        # Scrape from BBC
        for match in matches:
            if match['date'] < datetime(2021, 1, 1).date():
                raise Exception("Data doesn't go back that far for BBC cannot scrape this match")

            data = get_match_report(
                match["home_team_fullname"],
                match["away_team_fullname"],
                month=match['date'].strftime('%Y-%m'),
            )
            print(data)
    else:
        # Scrape from FBREF

        fixtures_df = retrieve_fixtures_table(season)
        for index, row in fixtures_df.iterrows():
            match_id = get_match_id(row["Home Team"], row["Away Team"])        
            if not match_id:
                raise Exception(f"Could not find match ID for row {index}")

            lineup = get_lineups(match_id)
            if lineup:
                print(f"Lineup for match {match_id} already exists.")
                continue
            else:
                print(f"Scraping match report for {match_id}.")

                try:
                    data = scrape_match_report(row["Match Report"])
                    time.sleep(random.randint(3, 6))
                except:
                    exception = traceback.format_exc()
                    print(f"Error scraping match report for row {index}: {row['Match Report']}")
                    print(f"\nException: {exception}\n")
                    sys.exit(1)



if __name__ == "__main__":
    scrape_lineups("2014-2015", 1)
