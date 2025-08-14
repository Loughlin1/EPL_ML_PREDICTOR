import datetime
import pandas as pd
import logging
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.db.models import Match
from app.services.models import predict as predictor
from app.services.web_scraping.superbru.submit_predictions import submit_to_superbru
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_upcoming_matches(session: Session) -> list[dict]:
    """Get upcoming matches from the database for the next hour."""
    now = datetime.datetime.now()
    next_hour = now + datetime.timedelta(hours=1)
    matches = (
        session.query(Match)
        .filter(Match.season == "2024-2025")
        .filter(Match.time >= now, Match.time < next_hour)
        .all()
    )
    return [match.to_dict() for match in matches]



def predict_results(matches: list, logger):
    """Predict results for each match using model."""
    matches = pd.DataFrame(matches)
    predictions = predictor.get_predictions(matches, logger=logger)
    return predictions


def main():
    with get_session() as session:
        # Refresh matches data
        matches = get_upcoming_matches(session)
        if not matches:
            print("No matches starting in the next hour.")
            return
        week = matches[0]["week"]
        predictions = predict_results(matches, logger=logger)
        submit_to_superbru(predictions, week=week)


if __name__ == "__main__":
    main()
