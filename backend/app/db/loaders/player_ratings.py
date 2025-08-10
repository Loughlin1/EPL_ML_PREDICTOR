import pandas as pd
from ..database import get_session
from ..models import Player, PlayerRating


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
            player = Player(name=player_name)
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
                print(f"Rating exists for {row.get('Name')} in {season}.")
                continue
            try:
                rating = PlayerRating(
                    player_id=player_id,
                    season=season,
                    rat=row.get("RAT"),
                    pos=row.get("POS"),
                    ver=row.get("VER"),
                    ps=row.get("PS"),
                    ski=row.get("SKI"),
                    wf=row.get("WF"),
                    wr=row.get("WR"),
                    pac=row.get("PAC"),
                    sho=row.get("SHO"),
                    pas=row.get("PAS"),
                    dri=row.get("DRI"),
                    def_=row.get("DEF"),
                    phy=row.get("PHY"),
                    bs=row.get("BS"),
                    igs=row.get("IGS")
                )
                session.add(rating)
            except Exception as e:
                print(f"Error processing row for {row.get('Name')} in {season}: {e}")
                continue
        session.commit()
