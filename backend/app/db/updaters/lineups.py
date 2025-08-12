import pandas as pd
from datetime import datetime
from sqlalchemy import select
from ..database import get_session
from ..models import Match, Team, Player, MatchLineup
from ..services.data_processing.data_loader import load_json_file
from ..core.paths import data_dir
from .upsert_team import upsert_team
from ..loaders.add_player_ratings import add_players


def upsert_lineups(
    season: str,
    df: pd.DataFrame = None,
    match_data: dict = None,
    date: str = None,
    home_team: str = None,
    away_team: str = None,
) -> None:
    """
    Upsert lineups into the match_lineups table from a DataFrame or match data dictionary.

    Args:
        season: Season string (e.g., "2023-2024").
        df: DataFrame with lineup data (columns: Date, Home, Away, home_formation, away_formation,
            home_starting_lineup, away_starting_lineup, home_bench, away_bench).
        match_data: Dictionary from prematch_lineups_scraper (keys: home_formation, away_formation,
            home_starting_lineup, home_subs_list, away_starting_lineup, away_subs_list).
        date: Match date (e.g., "2025-05-01") for single match.
        home_team: Home team name for single match.
        away_team: Away team name for single match.
    """
    # Load team name mappings
    try:
        team_name_mapping = load_json_file(f"{data_dir}/team_names_mapping.json")
    except FileNotFoundError:
        print(
            "Warning: team_names_mapping.json not found. Assuming exact team name matches."
        )
        team_name_mapping = {}

    with get_session() as session:
        # Get team IDs
        all_teams = session.execute(select(Team.name, Team.team_id)).all()
        team_map = {t.name: t.team_id for t in all_teams}

        # Process input: DataFrame or single match
        if df is not None:
            required_columns = [
                "Date",
                "Home",
                "Away",
                "home_formation",
                "away_formation",
                "home_starting_lineup",
                "away_starting_lineup",
                "home_bench",
                "away_bench",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(
                    f"Error: Missing required columns {missing_columns} for season {season}"
                )
                return
            rows = df.iterrows()
        elif match_data is not None and date and home_team and away_team:
            # Convert match_data to DataFrame-like structure
            rows = [
                (
                    0,
                    pd.Series(
                        {
                            "Date": date,
                            "Home": home_team,
                            "Away": away_team,
                            "home_formation": match_data.get("home_formation"),
                            "away_formation": match_data.get("away_formation"),
                            "home_starting_lineup": match_data.get(
                                "home_starting_lineup", []
                            ),
                            "away_starting_lineup": match_data.get(
                                "away_starting_lineup", []
                            ),
                            "home_bench": match_data.get("home_subs_list", []),
                            "away_bench": match_data.get("away_subs_list", []),
                        }
                    ),
                )
            ]
        else:
            print(
                "Error: Must provide either 'df' or 'match_data' with 'date', 'home_team', and 'away_team'."
            )
            return

        # Ensure teams exist
        team_names = set()
        if df is not None:
            team_names.update(df["Home"].dropna().unique())
            team_names.update(df["Away"].dropna().unique())
        else:
            team_names.update([home_team, away_team])
        team_df = pd.DataFrame({"Name": list(team_names)})
        upsert_team(df=team_df)

        # Refresh team map after upsert
        all_teams = session.execute(select(Team.name, Team.team_id)).all()
        team_map = {t.name: t.team_id for t in all_teams}

        # Collect all player names for upsert
        all_players = set()
        for _, row in rows:
            all_players.update(row.get("home_starting_lineup", []))
            all_players.update(row.get("away_starting_lineup", []))
            all_players.update(row.get("home_bench", []))
            all_players.update(row.get("away_bench", []))
        player_df = pd.DataFrame({"Name": list(all_players)})
        player_map = add_players(player_df)

        for idx, row in rows:
            try:
                # Parse date
                date_str = row.get("Date")
                if pd.isna(date_str):
                    print(f"Skipping row {idx}: Missing Date.")
                    continue
                date = pd.to_datetime(date_str, errors="coerce").date()
                if date is None:
                    print(f"Skipping row {idx}: Invalid Date format '{date_str}'.")
                    continue

                # Normalize team names
                home_team = row.get("Home")
                away_team = row.get("Away")
                if pd.isna(home_team) or pd.isna(away_team):
                    print(f"Skipping row {idx} on {date}: Missing Home or Away team.")
                    continue
                home_team = team_name_mapping.get(home_team, home_team)
                away_team = team_name_mapping.get(away_team, away_team)

                home_team_id = team_map.get(home_team)
                away_team_id = team_map.get(away_team)
                if not home_team_id or not away_team_id:
                    print(
                        f"Skipping row {idx} on {date}: Team not found (Home='{home_team}', Away='{away_team}')."
                    )
                    continue

                # Find match
                match = session.execute(
                    select(Match).filter_by(
                        season=season,
                        date=date,
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                    )
                ).scalar_one_or_none()
                if not match:
                    print(
                        f"No match found for {home_team} vs {away_team} on {date} in season {season}."
                    )
                    continue

                # Process lineups for home and away teams
                for team_id, formation, starting_lineup, bench in [
                    (
                        home_team_id,
                        row.get("home_formation"),
                        row.get("home_starting_lineup", []),
                        row.get("home_bench", []),
                    ),
                    (
                        away_team_id,
                        row.get("away_formation"),
                        row.get("away_starting_lineup", []),
                        row.get("away_bench", []),
                    ),
                ]:
                    # Process starting lineup
                    for player_name in starting_lineup:
                        player_id = player_map.get(player_name)
                        if not player_id:
                            print(
                                f"Skipping player '{player_name}' for team_id={team_id}: Not found."
                            )
                            continue
                        lineup = session.execute(
                            select(MatchLineup).filter_by(
                                match_id=match.match_id,
                                team_id=team_id,
                                player_id=player_id,
                                is_starting=True,
                            )
                        ).scalar_one_or_none()
                        if lineup:
                            lineup.formation = formation
                            print(
                                f"Updated lineup for player_id={player_id} (starting) in match_id={match.match_id}."
                            )
                        else:
                            lineup = MatchLineup(
                                match_id=match.match_id,
                                team_id=team_id,
                                formation=formation,
                                is_starting=True,
                                player_id=player_id,
                            )
                            session.add(lineup)
                            print(
                                f"Created lineup for player_id={player_id} (starting) in match_id={match.match_id}."
                            )

                    # Process substitutes
                    for player_name in bench:
                        player_id = player_map.get(player_name)
                        if not player_id:
                            print(
                                f"Skipping player '{player_name}' for team_id={team_id}: Not found."
                            )
                            continue
                        lineup = session.execute(
                            select(MatchLineup).filter_by(
                                match_id=match.match_id,
                                team_id=team_id,
                                player_id=player_id,
                                is_starting=False,
                            )
                        ).scalar_one_or_none()
                        if lineup:
                            lineup.formation = formation
                            print(
                                f"Updated lineup for player_id={player_id} (sub) in match_id={match.match_id}."
                            )
                        else:
                            lineup = MatchLineup(
                                match_id=match.match_id,
                                team_id=team_id,
                                formation=formation,
                                is_starting=False,
                                player_id=player_id,
                            )
                            session.add(lineup)
                            print(
                                f"Created lineup for player_id={player_id} (sub) in match_id={match.match_id}."
                            )

            except Exception as e:
                print(f"Error processing row {idx} on {date_str}: {e}")
                continue

        session.commit()


if __name__ == "__main__":
    # Example: From lineups_scraper.py
    df = pd.read_csv(f"{data_dir}/lineups/2023-2024.csv")
    upsert_lineups(season="2023-2024", df=df)

    # Example: From prematch_lineups_scraper.py
    from ..services.web_scraping.players.prematch_lineups_scraper import (
        get_match_report,
    )

    match_data = get_match_report("Ipswich Town", "West Ham United")
    upsert_lineups(
        season="2024-2025",
        match_data=match_data,
        date="2025-05-01",
        home_team="Ipswich Town",
        away_team="West Ham United",
    )
