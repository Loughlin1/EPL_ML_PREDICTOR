import pandas as pd
from .database import engine, get_session


def get_seasons_fixtures(season: str) -> pd.DataFrame:
    """
    Retrieve fixtures for a given season as a DataFrame.

    Args:
        season: Season string (e.g., "2014-2015").

    Returns:
        pd.DataFrame: Fixtures data for the specified season.
    """
    query = """
    SELECT season, week, day, date, time, home_team_id, away_team_id, 
           home_goals, away_goals, result, attendance, venue, referee
    FROM matches
    WHERE season = :season
    """
    return pd.read_sql(query, engine, params={"season": season})

def get_players() -> pd.DataFrame:
    """
    Retrieve all players as a DataFrame.

    Returns:
        pd.DataFrame: Player data with player_id and name.
    """
    query = """
    SELECT *
    FROM players
    """
    return pd.read_sql(query, engine)

def get_players_ratings(season: str) -> pd.DataFrame:
    """
    Retrieve player ratings for a given season as a DataFrame.

    Args:
        season: Season string (e.g., "2014-2015").

    Returns:
        pd.DataFrame: Player ratings data with rating_id, player_id, season, and rat.
    """
    query = """
    SELECT *
    FROM player_ratings
    WHERE season = :season
    """
    return pd.read_sql(query, engine, params={"season": season})

def get_shooting_stats(team_id: str = None) -> pd.DataFrame:
    """
    Retrieve shooting stats for all matches or a specific season as a DataFrame.

    Args:
        season: Optional season string (e.g., "2014-2015"). If None, returns all seasons.

    Returns:
        pd.DataFrame: Shooting stats data with match_id and team_id.
    """
    query = """
    SELECT match_id, team_id
    FROM match_shooting_stats
    """
    if team_id:
        query += " WHERE team_id = :team_id"
    return pd.read_sql(query, engine, params={"team_id": team_id} if team_id else {})


def get_teams() -> list[dict]:
    """
    Retrieve all teams as a DataFrame.

    Returns:
        list[dict]: Team data with team_id, name, fullname, and fbref_team_id.
    """
    query = """
    SELECT team_id, name, fullname, fbref_team_id
    FROM teams
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records") if not df.empty else []


def get_team_details(team_identifier: str, by: str = "name") -> dict:
    """
    Retrieve details for a specific team as a DataFrame.

    Args:
        team_identifier: Identifier for the team (e.g., name, team_id, or fbref_team_id).
        by: Column to query by ("name", "team_id", or "fbref_team_id"). Defaults to "name".

    Returns:
        pd.DataFrame: Team details (team_id, name, fullname, fbref_team_id).
    """
    valid_columns = ["name", "team_id", "fbref_team_id"]
    if by not in valid_columns:
        raise ValueError(f"Invalid 'by' parameter. Must be one of {valid_columns}")

    query = """
    SELECT team_id, name, fullname, fbref_team_id
    FROM teams
    WHERE {} = :identifier
    """.format(by)
    df = pd.read_sql(query, engine, params={"identifier": team_identifier})
    return df.to_dict(orient="records")[0] if not df.empty else {}

