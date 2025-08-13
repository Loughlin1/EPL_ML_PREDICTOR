from .models import Player, Team, PlayerRating, Match, MatchShootingStat, Lineup
from .database import get_session
from typing import List, Dict, Any, Optional


def get_seasons_fixtures(
    season: str = None,
    week: int = None,
    home_team_id: int = None,
    away_team_id: int = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve fixtures for a given season, week, home team, and/or away team.

    Args:
        season (str, optional): The season to filter by.
        week (int, optional): The week to filter by.
        home_team_id (int, optional): The home team ID to filter by.
        away_team_id (int, optional): The away team ID to filter by.

    Returns:
        List[Dict[str, Any]]: List of fixture dictionaries with team names.
    """
    with get_session() as session:
        query = session.query(Match)
        if season:
            query = query.filter(Match.season == season)
        if week:
            query = query.filter(Match.week == week)
        if home_team_id:
            query = query.filter(Match.home_team_id == home_team_id)
        if away_team_id:
            query = query.filter(Match.away_team_id == away_team_id)
        results = query.all()
        # Return as list of dicts with team names
        return [m.to_dict() for m in results]


def get_players(name: str = None) -> List[Dict[str, Any]]:
    """
    Retrieve players, optionally filtered by name.

    Args:
        name (str, optional): The name of the player to filter by.

    Returns:
        List[Dict[str, Any]]: List of player dictionaries.
    """
    with get_session() as session:
        query = session.query(Player)
        if name:
            query = query.filter(Player.name == name)
        return [ p.to_dict() for p in query.all()]


def get_players_ratings(
    season: str = None, player_id: int = None
) -> List[Dict[str, Any]]:
    """
    Retrieve player ratings, optionally filtered by season and/or player ID.

    Args:
        season (str, optional): The season to filter by.
        player_id (int, optional): The player ID to filter by.

    Returns:
        List[Dict[str, Any]]: List of player rating dictionaries.
    """
    with get_session() as session:
        query = session.query(PlayerRating)
        if season:
            query = query.filter(PlayerRating.season == season)
        if player_id:
            query = query.filter(PlayerRating.player_id == player_id)
        return [r.to_dict() for r in query.all()]


def get_shooting_stats(
    team_id: int = None, match_id: int = None
) -> List[Dict[str, Any]]:
    """
    Retrieve shooting stats, optionally filtered by team ID and/or match ID.

    Args:
        team_id (int, optional): The team ID to filter by.
        match_id (int, optional): The match ID to filter by.

    Returns:
        List[Dict[str, Any]]: List of shooting stat dictionaries.
    """
    with get_session() as session:
        query = session.query(MatchShootingStat)
        if team_id:
            query = query.filter(MatchShootingStat.team_id == team_id)
        if match_id:
            query = query.filter(MatchShootingStat.match_id == match_id)
        return [s.to_dict() for s in query.all()]


def get_teams(
    name: str = None, team_id: int = None, fbref_team_id: str = None
) -> List[Dict[str, Any]]:
    """
    Retrieve teams, optionally filtered by name, team ID, or fbref team ID.

    Args:
        name (str, optional): The name of the team to filter by.
        team_id (int, optional): The team ID to filter by.
        fbref_team_id (str, optional): The fbref team ID to filter by.

    Returns:
        List[Dict[str, Any]]: List of team dictionaries.
    """
    with get_session() as session:
        query = session.query(Team)
        if name:
            query = query.filter(Team.name == name)
        if team_id:
            query = query.filter(Team.team_id == team_id)
        if fbref_team_id:
            query = query.filter(Team.fbref_team_id == fbref_team_id)
        return [t.to_dict() for t in query.all()]


def get_teams_names() -> List[str]:
    """
    Retrieve a list of all team names.

    Returns:
        List[str]: List of team names.
    """
    return [team["name"] for team in get_teams()]


def get_team_details(team_identifier: str = None, by: str = "name") -> Dict[str, Any]:
    """
    Retrieve details for a specific team by name, team ID, or fbref team ID.

    Args:
        team_identifier (str, optional): The identifier value for the team.
        by (str, optional): The field to filter by ("name", "team_id", "fbref_team_id").

    Returns:
        Dict[str, Any]: Dictionary of team details, or empty dict if not found.
    """
    if not team_identifier:
        return {}
    with get_session() as session:
        query = session.query(Team)
        if by == "name":
            query = query.filter(Team.name == team_identifier)
        elif by == "team_id":
            query = query.filter(Team.team_id == team_identifier)
        elif by == "fbref_team_id":
            query = query.filter(Team.fbref_team_id == team_identifier)
        team = query.first()
        return team.to_dict() if team else {}


def get_teams_by_season(seasons: list[str]) -> List[Dict[str, Any]]:
    """
    Retrieve a list of teams that played in a specific season.

    Args:
        seasons (list[str]): The seasons to filter by (e.g., "2024-2025").

    Returns:
        List[Dict[str, Any]]: List of team dictionaries for the given season.
    """
    with get_session() as session:
        # Query distinct home and away teams from matches in the given season
        home_teams = (
            session.query(Team)
            .join(Match, Team.team_id == Match.home_team_id)
            .filter(Match.season.in_(seasons))
            .distinct()
            .all()
        )
        away_teams = (
            session.query(Team)
            .join(Match, Team.team_id == Match.away_team_id)
            .filter(Match.season.in_(seasons))
            .distinct()
            .all()
        )
        # Combine and deduplicate teams
        teams = {t.team_id: t for t in home_teams + away_teams}
        return [t.to_dict() for t in teams.values()]


def get_match_id(season: str, week: str, home_team_id: int, away_team_id: int) -> int:
    """
    Get the match ID for a given season and team IDs.
    Args:
        season (str): The season of the match.
        home_team_id (int): The ID of the home team.
        away_team_id (int): The ID of the away team.
    Returns:
        int: The match ID for the given season and team IDs.
    """
    with get_session() as session:
        matches = session.query(Match).filter(
            Match.season == season,
            Match.week == week,
            Match.home_team_id == home_team_id,
            Match.away_team_id == away_team_id,
        ).first()
        return matches.match_id if matches else None


def get_lineups(season: str = None, week: int = None, match_id: int = None) -> list[dict]:
    """
    Get the lineups for a given season and week.
    Args:
        season (str): The season of the match.
        week (int): The week of the match.
        match_id (int): The ID of the match
    Returns:
        list[dict]: A list of dictionaries containing the lineups for the given filters
    """
    with get_session() as session:
        query = session.query(Lineup)
        if match_id is not None:
            query = query.filter(
                Lineup.match_id == match_id,
            )
        elif season is not None and week is not None:
            query = query.filter(
                Lineup.season == season,
                Lineup.week == week,
            )
        elif season is not None:
            query = query.filter(
                Lineup.season == season,
            )
        elif week is not None:
            query = query.filter(Lineup.week == week)

        lineups = query.all()       
        return [lineup.to_dict() for lineup in lineups]


if __name__ == "__main__":
    print(get_players(name="Nani"))
    print(get_teams_names())
    print(get_lineups())
    print(get_teams())