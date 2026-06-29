"""
Train a season-scoped model for every season that has enough historical data.

For each target season, the model is trained on all seasons *before* it.
The earliest trainable season is 2015-2016 (trained on 2014-2015 only).

Run from the backend directory:
    uv run python scripts/train_all_seasons.py

Or train a single season:
    uv run python scripts/train_all_seasons.py --season 2024-2025
"""

import argparse
import logging
import sys

sys.path.insert(0, ".")

from app.services.models.train import train_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Seasons that have fixture data in the DB (and at least one prior training season)
TRAINABLE_SEASONS = [
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
    "2025-2026",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--season",
        help="Train for a single season only (e.g. 2024-2025)",
        default=None,
    )
    args = parser.parse_args()

    seasons = [args.season] if args.season else TRAINABLE_SEASONS

    for season in seasons:
        logger.info(f"--- Training model for season {season} ---")
        try:
            train_pipeline(season=season)
            logger.info(f"Saved model_{season}.joblib and scaler_{season}.pkl")
        except Exception as e:
            logger.error(f"Failed for season {season}: {e}")

    logger.info("Done.")


if __name__ == "__main__":
    main()
