import pandas as pd
from .database import engine

def flexible_query(table: str, filters: dict = None, columns: list = None) -> pd.DataFrame:
    """
    General-purpose query builder for filtering any table.

    Args:
        table: Table name.
        filters: Dict of column-value pairs to filter by.
        columns: List of columns to select (default: all).

    Returns:
        pd.DataFrame: Query results.
    """
    select_cols = ", ".join(columns) if columns else "*"
    query = f"SELECT {select_cols} FROM {table}"
    params = {}
    if filters:
        where_clauses = []
        for col, val in filters.items():
            where_clauses.append(f"{col} = :{col}")
            params[col] = val
        query += " WHERE " + " AND ".join(where_clauses)
    return pd.read_sql(query, engine, params=params)

def get_seasons_fixtures(season: str = None, week: int = None, home_team_id: int = None, away_team_id: int = None) -> pd.DataFrame:
    filters = {}
    if season: filters["season"] = season
    if week: filters["week"] = week
    if home_team_id: filters["home_team_id"] = home_team_id
    if away_team_id: filters["away_team_id"] = away_team_id
    columns = ["season", "week", "day", "date", "time", "home_team_id", "away_team_id", "home_goals", "away_goals", "result", "attendance", "venue", "referee"]
    return flexible_query("matches", filters, columns)

def get_players(name: str = None) -> pd.DataFrame:
    filters = {}
    if name: filters["name"] = name
    return flexible_query("players", filters)

def get_players_ratings(season: str = None, player_id: int = None) -> pd.DataFrame:
    filters = {}
    if season: filters["season"] = season
    if player_id: filters["player_id"] = player_id
    return flexible_query("player_ratings", filters)

def get_shooting_stats(team_id: str = None, match_id: int = None) -> pd.DataFrame:
    filters = {}
    if team_id: filters["team_id"] = team_id
    if match_id: filters["match_id"] = match_id
    columns = ["match_id", "team_id"]
    return flexible_query("match_shooting_stats", filters, columns)

def get_teams(name: str = None, team_id: int = None, fbref_team_id: str = None) -> list[dict]:
    filters = {}
    if name: filters["name"] = name
    if team_id: filters["team_id"] = team_id
    if fbref_team_id: filters["fbref_team_id"] = fbref_team_id
    columns = ["team_id", "name", "fullname", "fbref_team_id"]
    df = flexible_query("teams", filters, columns)
    return df.to_dict(orient="records") if not df.empty else []

def get_team_details(team_identifier: str = None, by: str = "name") -> dict:
    if not team_identifier:
        return {}
    filters = {by: team_identifier}
    columns = ["team_id", "name", "fullname", "fbref_team_id"]
    df = flexible_query("teams", filters, columns)
    return df.to_dict(orient="records")[0] if not df.empty else {}


if __name__ == "__main__":
    print(get_players(name="Nani"))