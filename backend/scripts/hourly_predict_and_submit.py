import datetime
import pandas as pd
import logging
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.db.models import Match
from app.services.models import predict as predictor
from app.services.web_scraping.lineups.prematch_lineups_scraper import (
    scrape_lineups_for_match,
)
from app.services.web_scraping.superbru.submit_predictions import submit_to_superbru

from app.db.updaters.lineups import upsert_lineups
from app.core.config import settings

logger = logging.getLogger(__name__)


# 1. Query matches starting in the next hour
def get_upcoming_matches(session: Session) -> list[dict]:
    now = datetime.datetime.now()
    next_hour = now + datetime.timedelta(hours=1)
    matches = (
        session.query(Match)
        .filter(Match.season == "2024-2025")
        # .filter(Match.time >= now, Match.time < next_hour)
        .all()
    )
    return [match.to_dict() for match in matches]


# 2. Scrape lineups for each match
def get_and_save_lineups_for_matches(matches: list[dict]) -> None:
    for match in matches:
        data = scrape_lineups_for_match(
            match["home_team_fullname"],
            match["away_team_fullname"],
            month=match["date"].strftime("%Y-%m"),
        )
        upsert_lineups(
            season=settings.CURRENT_SEASON,
            match_data=data,
            date=match["date"],
            home_team=match["home_team"],
            away_team=match["away_team"],
        )

    print("Lineups saved successfully.")


# 3. Predict results using your model
def predict_results(matches: list, logger):
    # Prepare input for your model
    matches = pd.DataFrame(matches)
    predictions = predictor.get_predictions(matches, logger=logger)
    return predictions


def main():
    with get_session() as session:
        # Refresh matches data
        matches = get_upcoming_matches(session)
        print(matches[0])
        if not matches:
            print("No matches starting in the next hour.")
            return
        week = matches[0]["week"]
        get_and_save_lineups_for_matches(matches)
        # predictions = predict_results(matches, logger=logger)
        # submit_to_superbru(predictions, week=week)


if __name__ == "__main__":
    main()
