import pandas as pd
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_session, SessionLocal
from ..models import Player, PlayerRating


def clean_player_name(name: str) -> str:
    """
    Clean player name by removing numeric prefix and optional suffix.

    Args:
        name: Raw player name (e.g., "56 Leon Chiwome Normal").

    Returns:
        Cleaned name (e.g., "Leon Chiwome") or original if no match.
    """
    # Match: number, space, name, optional (space, word)
    match = re.match(r"^\d+\s+(.+?)(?:\s+\w+)?$", name)
    return match.group(1).strip() if match else name.strip()


def generate_initials(name: str) -> str:
    """
    Generate initials from a player name.

    Args:
        name: Player name (e.g., "Harry Kane", "Leon Chiwome").

    Returns:
        Initials (e.g., "H. Kane", "L. Chiwome").
    """
    if not name or not isinstance(name, str):
        return None
    parts = name.strip().split()
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0][0]}. {parts[-1]}"


def add_players(df: pd.DataFrame) -> dict:
    """Add players from DataFrame to the players table.

    Args:
        df: DataFrame with player data (Name column).

    Returns:
        dict: Mapping of player names to player_id.
    """
    expected_columns = ["Name"]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in DataFrame: {missing_columns}")

    players = set(df.get("Name", pd.Series([])).dropna().unique())
    player_map = {}
    with get_session() as session:
        for player_name in players:
            existing_player = session.query(Player).filter_by(name=player_name).first()
            if existing_player:
                player_map[player_name] = existing_player.player_id
                continue
            player = Player(name=player_name,initials=generate_initials(player_name))
            session.add(player)
            session.flush()
            player_map[player_name] = player.player_id
        session.commit()
    return player_map


def add_ratings(df: pd.DataFrame, season: str, player_map: dict) -> None:
    """Add player ratings from DataFrame to the player_ratings table.

    Args:
        df: DataFrame with player ratings (Name, RAT, POS, etc.).
        season: Season string (e.g., "2014-2015").
        player_map: Dict mapping player names to player_id.
    """
    # Define column mapping
    column_mapping = {
        "Name": "Name",
        "RATOrder By Rating": "RAT",
        "POS Order By Position": "POS",
        "PriceOrder By Price": "VER",
        "PriceOrder By Price.1": "PS",
        "FOOTOrder By FOOT": None,
        "WFOrder By Weak Foot": "WF",
        "SMOrder By Skills": "SKI",
        "WRAttack / Defense": "WR",
        "PACOrder By Pace": "PAC",
        "SHOOrder By Shooting": "SHO",
        "PASOrder By Passing": "PAS",
        "DRIOrder By Dribbling": "DRI",
        "DEFOrder By Defending": "DEF",
        "PHYOrder By Physical": "PHY",
        "POPOrder By Popularity": "Unnamed: 14",
        "BodyOrder By Height": "Unnamed: 15",
        "IGSOrder By IGS": "IGS",
        "Unnamed: 18": "Unnamed: 18",
    }

    # Rename columns
    df = df.rename(columns={k: v for k, v in column_mapping.items() if v is not None})
    df.dropna(thresh=6, inplace=True) # Remove empty rows

    expected_columns = [
        "Name", "RAT", "POS", "VER", "PS", "SKI", "WF", "WR", "PAC",
        "SHO", "PAS", "DRI", "DEF", "PHY", "BS", "IGS"
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in DataFrame for season {season}: {missing_columns}")

    with get_session() as session:
        for _, row in df.iterrows():
            if "Name" not in df.columns or pd.isna(row.get("Name")):
                print(f"Skipping row: Missing or invalid Name.")
                continue
            player_id = player_map.get(row.get("Name"))
            if not player_id:
                print(f"Player {row.get('Name')} not found.")
                continue
            existing_rating = session.query(PlayerRating).filter_by(
                player_id=player_id, season=season
            ).first()
            if existing_rating:
                # print(f"Rating exists for {row.get('Name')} in {season}.")
                continue
            try:
                rating = PlayerRating(
                    player_id=player_id,
                    season=season,
                    rating=row.get("RAT"),
                    position=row.get("POS"),
                    version=row.get("VER"),
                    psprice=row.get("PS"),
                    skill=row.get("SKI"),
                    weakfoot=row.get("WF"),
                    workrate=row.get("WR"),
                    pace=row.get("PAC"),
                    shooting=row.get("SHO"),
                    passing=row.get("PAS"),
                    dribbling=row.get("DRI"),
                    defense=row.get("DEF"),
                    physical=row.get("PHY"),
                    basestats=row.get("BS"),
                    ingamestats=row.get("IGS")
                )
                session.add(rating)
            except Exception as e:
                print(f"Error processing row for {row.get('Name')} in {season}: {e}")
                continue
        session.commit()
