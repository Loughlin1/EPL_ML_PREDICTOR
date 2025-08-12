import pandas as pd
from datetime import datetime
from ..database import get_session
from ..models import Team, Match


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


def add_teams(
    df: pd.DataFrame, team_full_name_mapping: dict, team_ids_mapping: dict
) -> dict:
    """Add teams from DataFrame and JSON mappings to the teams table.

    Args:
        df: DataFrame with Home and Away columns.
        team_full_name_mapping: Dict mapping team names to full names.
        team_ids_mapping: Dict mapping full names (with dashes) to fbref_team_id.

    Returns:
        dict: Mapping of team names to team_id.
    """
    expected_columns = ["Home", "Away"]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in DataFrame: {missing_columns}")

    teams = set()
    teams.update(df.get("Home", pd.Series([])).dropna().unique())
    teams.update(df.get("Away", pd.Series([])).dropna().unique())

    team_map = {}
    with get_session() as session:
        for team_name in teams:
            # Check for existing team
            existing_team = session.query(Team).filter_by(name=team_name).first()
            if existing_team:
                team_map[team_name] = existing_team.team_id
                continue

            fullname = team_full_name_mapping.get(team_name, team_name)
            fbref_team_id = team_ids_mapping.get(fullname.replace(" ", "-"), "unknown")
            team = Team(name=team_name, fullname=fullname, fbref_team_id=fbref_team_id)
            session.add(team)
            session.flush()
            team_map[team_name] = team.team_id
        session.commit()
    return team_map


def add_matches(df: pd.DataFrame, season: str, team_map: dict) -> dict:
    """Add matches from DataFrame to the matches table.

    Args:
        df: DataFrame with match data (Date, Wk, Day, Time, Home, Away, Score, etc.).
        season: Season string (e.g., "2014-2015").
        team_map: Dict mapping team names to team_id.

    Returns:
        dict: Mapping of (date, home_team_id) to match_id.
    """
    expected_columns = [
        "Date",
        "Wk",
        "Day",
        "Time",
        "Home",
        "Away",
        "Score",
        "Attendance",
        "Venue",
        "Referee",
        "Match Report",
        "Notes",
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(
            f"Warning: Missing columns in DataFrame for season {season}: {missing_columns}"
        )

    match_map = {}
    with get_session() as session:
        for _, row in df.iterrows():
            if "Date" not in df.columns or pd.isna(row.get("Date")):
                print(f"Skipping row: Missing or invalid Date.")
                continue
            try:
                date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                home_team_id = team_map.get(row.get("Home"))
                away_team_id = team_map.get(row.get("Away"))
                if not (home_team_id and away_team_id):
                    print(
                        f"Skipping row for {row.get('Home', 'unknown')} vs {row.get('Away', 'unknown')} on {date}: Team not found."
                    )
                    continue

                # Check for existing match
                existing_match = (
                    session.query(Match)
                    .filter_by(
                        season=season,
                        date=date,
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                    )
                    .first()
                )
                if existing_match:
                    match_map[(date, home_team_id)] = existing_match.match_id
                    continue

                home_goals, away_goals, result = parse_score(row.get("Score"))
                match = Match(
                    season=season,
                    week=row.get("Wk"),
                    day=row.get("Day"),
                    date=date,
                    time=datetime.strptime(row["Time"], "%H:%M").time()
                    if pd.notna(row.get("Time"))
                    else None,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_goals=home_goals,
                    away_goals=away_goals,
                    result=result,
                    attendance=int(row.get("Attendance"))
                    if pd.notna(row.get("Attendance"))
                    else None,
                    venue=row.get("Venue"),
                    referee=row.get("Referee"),
                    match_report=row.get("Match Report"),
                    notes=row.get("Notes"),
                )
                session.add(match)
                session.flush()
                match_map[(date, home_team_id)] = match.match_id
            except Exception as e:
                print(
                    f"Error processing row for {season} on {row.get('Date', 'unknown')}: {e}"
                )
                continue
        session.commit()
    return match_map
