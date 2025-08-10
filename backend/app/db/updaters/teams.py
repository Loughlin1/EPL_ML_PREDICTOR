import pandas as pd
from sqlalchemy import select
from ..database import get_session
from ..models import Team
from ..mappings.load_mappings import load_team_name_mapping, load_team_ids_mapping
from ...core.paths import data_dir

def upsert_team(name: str = None, fullname: str = None, fbref_team_id: str = None, df: pd.DataFrame = None) -> None:
    """
    Upsert a team or teams into the teams table. Creates new teams if they don't exist,
    updates existing teams with new fullname or fbref_team_id if provided.

    Args:
        name: Team name (e.g., "Arsenal"). Required if df is None.
        fullname: Full team name (e.g., "Arsenal FC"). Optional.
        fbref_team_id: FBref team ID (e.g., "18bb7c10"). Optional.
        df: DataFrame with team data (columns: Name, Fullname, FBrefTeamID). Optional.
    """
    # Load mappings
    team_name_mapping = load_team_name_mapping()
    team_ids_mapping = load_team_ids_mapping()

    with get_session() as session:
        if df is not None:
            # Batch mode: Process DataFrame
            expected_columns = ["Name", "Fullname", "FBrefTeamID"]
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                print(f"Warning: Missing columns in DataFrame: {missing_columns}")

            if "Name" not in df.columns:
                print("Error: DataFrame must contain 'Name' column.")
                return

            for idx, row in df.iterrows():
                try:
                    team_name = row.get("Name")
                    if pd.isna(team_name):
                        print(f"Skipping row {idx}: Missing Name.")
                        continue

                    # Normalize team name
                    team_name = team_name_mapping.get(team_name, team_name)
                    row_fullname = row.get("Fullname", team_name)
                    row_fbref_id = row.get("FBrefTeamID", team_ids_mapping.get(row_fullname.replace(" ", "-")))

                    # Upsert team
                    team = session.execute(
                        select(Team).filter_by(name=team_name)
                    ).scalar_one_or_none()

                    if team:
                        # Update existing team
                        team.fullname = row_fullname if pd.notna(row_fullname) else team.fullname
                        team.fbref_team_id = row_fbref_id if pd.notna(row_fbref_id) else team.fbref_team_id
                        print(f"Updated team '{team_name}' (team_id={team.team_id}).")
                    else:
                        # Create new team
                        team = Team(
                            name=team_name,
                            fullname=row_fullname if pd.notna(row_fullname) else team_name,
                            fbref_team_id=row_fbref_id if pd.notna(row_fbref_id) else None
                        )
                        session.add(team)
                        print(f"Created new team '{team_name}'.")

                except Exception as e:
                    print(f"Error processing row {idx} for team '{team_name}': {e}")
                    continue

        elif name:
            # Single team mode
            team_name = team_name_mapping.get(name, name)
            default_fullname = fullname or team_name
            default_fbref_id = fbref_team_id or team_ids_mapping.get(default_fullname.replace(" ", "-"))

            team = session.execute(
                select(Team).filter_by(name=team_name)
            ).scalar_one_or_none()

            if team:
                # Update existing team
                team.fullname = fullname if fullname else team.fullname
                team.fbref_team_id = fbref_team_id if fbref_team_id else team.fbref_team_id
                print(f"Updated team '{team_name}' (team_id={team.team_id}).")
            else:
                # Create new team
                team = Team(
                    name=team_name,
                    fullname=fullname if fullname else team_name,
                    fbref_team_id=fbref_team_id if fbref_team_id else default_fbref_id
                )
                session.add(team)
                print(f"Created new team '{team_name}'.")

        else:
            print("Error: Must provide either 'name' or 'df'.")
            return

        session.commit()

if __name__ == "__main__":
    # Example usage: Single team
    upsert_team(name="Ipswich Town")

    # Example usage: DataFrame
    # df = pd.DataFrame({
    #     "Name": ["Brighton", "Leicester"],
    #     "Fullname": ["Brighton & Hove Albion", "Leicester City"],
    #     "FBrefTeamID": ["d07537b9", "a2d435b3"]
    # })
    # upsert_team(df=df)
