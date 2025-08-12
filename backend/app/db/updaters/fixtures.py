import pandas as pd
from datetime import datetime
from sqlalchemy import select
from ..database import get_session
from ..models import Match, Team
from fuzzywuzzy import process

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


def upsert_fixtures(df: pd.DataFrame, season: str) -> None:
    """
    Upsert fixtures in the matches table from a DataFrame. Creates new matches if they don't exist,
    updates existing matches with new results.

    Args:
        df: DataFrame with match data (expected columns: Date, Home, Away, Score, week, Day, Time, etc.).
        season: Season string (e.g., "2023-2024").
    """
    # Define expected columns
    expected_columns = ["Date", "Home", "Away", "Score"]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in DataFrame for season {season}: {missing_columns}")

    # Ensure required columns exist
    required_columns = ["Date", "Home", "Away", "Score"]
    if not all(col in df.columns for col in required_columns):
        print(f"Error: Missing required columns {required_columns} for season {season}")
        return

    with get_session() as session:
        # Get team IDs with fuzzy matching
        all_teams = session.execute(select(Team.name, Team.team_id)).all()
        team_map = {t.name: t.team_id for t in all_teams}
        team_names = list(team_map.keys())

        for idx, row in df.iterrows():
            try:
                # Parse date
                date_str = row.get("Date")
                if pd.isna(date_str):
                    print(f"Skipping row {idx}: Missing Date.")
                    continue
                date = pd.to_datetime(date_str, errors='coerce').date()
                if date is None:
                    print(f"Skipping row {idx}: Invalid Date format '{date_str}'.")
                    continue

                # Fuzzy match team names
                home_team = row.get("Home")
                away_team = row.get("Away")
                if pd.isna(home_team) or pd.isna(away_team):
                    print(f"Skipping row {idx} on {date}: Missing Home or Away team.")
                    continue

                home_match, home_score = process.extractOne(home_team, team_names) if team_names else (None, 0)
                away_match, away_score = process.extractOne(away_team, team_names) if team_names else (None, 0)
                if home_score < 80:
                    print(f"Skipping row {idx} on {date}: No close match for Home='{home_team}' {home_match=}.")
                    continue
                if away_score < 80:
                    print(f"Skipping row {idx} on {date}: No close match for Away='{away_team}' {away_match=}.")
                    continue

                home_team_id = team_map.get(home_match)
                away_team_id = team_map.get(away_match)

                # Find existing match
                match = session.execute(
                    select(Match)
                    .filter_by(season=season, date=date, home_team_id=home_team_id, away_team_id=away_team_id)
                ).scalar_one_or_none()


                # Parse score (for both update and insert)
                home_goals, away_goals, result = parse_score(row.get("Score"))

                if match:
                    # Update existing match
                    if home_goals is not None:
                        match.home_goals = home_goals
                        match.away_goals = away_goals
                        match.result = result
                    # Update other fields if provided
                    match.week = row.get("week", match.week)
                    match.day = row.get("Day", match.day)
                    match.time = datetime.strptime(row["Time"], "%H:%M").time() if pd.notna(row.get("Time")) else match.time
                    match.attendance = int(row.get("Attendance")) if pd.notna(row.get("Attendance")) else match.attendance
                    match.venue = row.get("Venue", match.venue)
                    match.referee = row.get("Referee", match.referee)
                    match.match_report = row.get("Match Report", match.match_report)
                    match.notes = row.get("Notes", match.notes)
                    print(f"Updated match_id={match.match_id} for {home_team} vs {away_team} on {date}.")
                else:
                    # Create new match
                    match = Match(
                        season=season,
                        week=row.get("week"),
                        day=row.get("Day"),
                        date=date,
                        time=datetime.strptime(row["Time"], "%H:%M").time() if pd.notna(row.get("Time")) else None,
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        home_goals=home_goals,
                        away_goals=away_goals,
                        result=result,
                        attendance=int(row.get("Attendance")) if pd.notna(row.get("Attendance")) else None,
                        venue=row.get("Venue"),
                        referee=row.get("Referee"),
                        match_report=row.get("Match Report"),
                        notes=row.get("Notes")
                    )
                    session.add(match)
                    print(f"Created new match for {home_team} vs {away_team} on {date}.")

            except Exception as e:
                print(f"Error processing row {idx} on {date_str}: {e}")
                continue

        session.commit()


if __name__ == "__main__":
    # Example usage
    df = pd.read_csv("../../data/season_2023.csv")
    update_match_results(df, season="2023-2024")