import pandas as pd
from datetime import datetime

from ..database import get_session, create_tables
from ..models import Team, Match, MatchShootingStat, Player, PlayerRating
from ...services.data_processing.data_loader import generate_seasons, load_json_file
from ...core.paths import (
    backend_dir,
    data_dir,
    FIXTURES_TRAINING_DATA_DIR,
    SHOOTING_TEST_DATA_DIR,
)
from ..queries import get_teams, get_shooting_stats, get_team_details
from .shooting_stats import add_shooting_stats
from .player_ratings import add_players, add_ratings
from .fixtures import add_teams, add_matches
from ..mappings.load_mappings import load_team_ids_mapping, load_team_name_mapping


def import_historical_fixtures(start_year: int = 2014, end_year: int = 2024) -> None:
    """
    Load historical fixtures data from CSVs and JSON mappings into teams and matches tables.

    Args:
        start_year: Start year for seasons (e.g., 2014).
        end_year: End year for seasons (e.g., 2023).
    """
    create_tables()
    seasons = generate_seasons(start_year, end_year)
    team_full_name_mapping = load_team_name_mapping()
    team_ids_mapping = load_team_ids_mapping()

    # Load all fixtures to collect teams
    all_dfs = []
    for season in seasons:
        try:
            df = pd.read_csv(f"{FIXTURES_TRAINING_DATA_DIR}/{season}.csv")
            df = df.dropna(thresh=6)
            all_dfs.append(df)
        except FileNotFoundError:
            print(f"No fixtures data for {season}")
            continue

    if not all_dfs:
        print("No fixtures data found.")
        return

    # Add teams
    combined_df = pd.concat(all_dfs, ignore_index=True)
    team_map = add_teams(combined_df, team_full_name_mapping, team_ids_mapping)

    # Add matches
    for season, df in zip(seasons, all_dfs):
        add_matches(df, season, team_map)


def import_fifa_ratings(start_year: int = 2014, end_year: int = 2021) -> None:
    """
    Load player ratings from FIFA CSVs into players and player_ratings tables.

    Args:
        start_year: Start year for seasons (e.g., 2014).
        end_year: End year for seasons (e.g., 2021).
    """
    create_tables()
    seasons = generate_seasons(start_year, end_year)

    # Load all CSVs to collect players
    all_dfs = []
    for year in range(start_year + 1, end_year + 2):
        try:
            df = pd.read_csv(
                f"{data_dir}/player_ratings/epl_players_fifa{year%100:02d}.csv"
            )
            all_dfs.append(df)
        except FileNotFoundError:
            print(f"No player ratings for FIFA{year%100:02d}")
            continue

    if not all_dfs:
        print("No player ratings data found.")
        return

    # Add players
    combined_df = pd.concat(all_dfs, ignore_index=True)
    player_map = add_players(combined_df)

    # Add ratings
    for season, year in zip(seasons, range(start_year + 1, end_year + 2)):
        try:
            df = pd.read_csv(
                f"{data_dir}/player_ratings/epl_players_fifa{year%100:02d}.csv"
            )
            add_ratings(df, season, player_map)
        except FileNotFoundError:
            print(f"No player ratings for FIFA{year%100:02d}")
            continue


def import_shooting_stats(start_year: int = 2014, end_year: int = 2024) -> None:
    create_tables()
    seasons = generate_seasons(start_year, end_year)
    teams = get_teams()
    for team in teams:
        name = team["name"]
        df = pd.read_csv(f"{data_dir}/shooting_stats/{name.replace(' ', '-')}.csv")
        add_shooting_stats(df, name, seasons)


if __name__ == "__main__":
    import_historical_fixtures()
    import_fifa_ratings()
    import_shooting_stats()
