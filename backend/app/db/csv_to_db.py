import pandas as pd
from datetime import datetime

from .database import get_session, create_tables
from .models import Team, Match
from ..services.data_processing.data_loader import generate_seasons
from ..core.paths import FIXTURES_TRAINING_DATA_DIR


def parse_score(score):
    """Parse score (e.g., '2–1') into home_goals, away_goals, result."""
    if pd.isna(score) or score == "":
        return None, None, None
    try:
        home, away = map(int, score.split("–"))
        result = "H" if home > away else "A" if away > home else "D"
        return home, away, result
    except (ValueError, AttributeError):
        return None, None, None

def import_historical_data():
    create_tables()  # Ensure tables exist
    with get_session() as session:
        seasons = generate_seasons(start_year=2014, end_year=2023)
        # Load and insert teams
        teams = set()
        for season in seasons:
            df = pd.read_csv(f"{FIXTURES_TRAINING_DATA_DIR}/{season}.csv")
            df = df.dropna(thresh=6)
            teams.update(df["Home"].unique())
            teams.update(df["Away"].unique())

        team_map = {}
        for team_name in teams:
            team = Team(name=team_name)
            session.add(team)
            session.flush()  # Get team_id
            team_map[team_name] = team.team_id

        # Import matches
        for season in seasons:
            df = pd.read_csv(f"{FIXTURES_TRAINING_DATA_DIR}/{season}.csv")
            df = df.dropna(thresh=6)
            for _, row in df.iterrows():
                home_goals, away_goals, result = parse_score(row["Score"])
                match = Match(
                    season=season,
                    week=row["Wk"] if pd.notna(row["Wk"]) else None,
                    day=row["Day"] if pd.notna(row["Day"]) else None,
                    date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),  # Adjust format if needed
                    time=datetime.strptime(row["Time"], "%H:%M").time() if pd.notna(row["Time"]) else None,
                    home_team_id=team_map[row["Home"]],
                    away_team_id=team_map[row["Away"]],
                    home_goals=home_goals,
                    away_goals=away_goals,
                    result=result,
                    attendance=int(row["Attendance"]) if pd.notna(row["Attendance"]) else None,
                    venue=row["Venue"] if pd.notna(row["Venue"]) else None,
                    referee=row["Referee"] if pd.notna(row["Referee"]) else None,
                    match_report=row["Match Report"] if pd.notna(row["Match Report"]) else None,
                    notes=row["Notes"] if pd.notna(row["Notes"]) else None
                )
                session.add(match)


if __name__ == "__main__":
    import_historical_data()