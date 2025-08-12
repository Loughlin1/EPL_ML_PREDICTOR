from sqlalchemy import select
from ..database import get_session
from ..models import Match, Team, MatchShootingStat
from datetime import datetime
import pandas as pd


def add_shooting_stats(df: pd.DataFrame, team_name: str, seasons: list[str]) -> None:
    """
    Add shooting stats from a DataFrame to the match_shooting_stats table.

    Args:
        df: DataFrame with shooting stats (columns: Date, Venue, Opponent, etc.).
        team_name: Name of the team (e.g., "Arsenal").
        seasons: List of seasons (e.g., ["2013-2014", "2014-2015"]).
    """
    if not isinstance(df, pd.DataFrame):
        print("Argument `df` is not a pandas DataFrame")
        return

    expected_columns = [
        "Date",
        "Round",
        "Day",
        "Venue",
        "Result",
        "GF",
        "GA",
        "Opponent",
        "Sh",
        "SoT",
        "SoT%",
        "G/Sh",
        "G/SoT",
        "Dist",
        "PK",
        "PKatt",
        "FK",
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(
            f"Warning: Missing columns in DataFrame for {team_name} in {seasons}: {missing_columns}"
        )

    df = df.dropna(subset=["Date"])  # Filter out rows with missing values

    with get_session() as session:
        # Get team_id
        team = session.execute(
            select(Team).filter_by(name=team_name)
        ).scalar_one_or_none()
        if not team:
            print(f"Team {team_name} not found.")
            return

        team_id = team.team_id

        # Create a map of matches for lookup
        matches = session.execute(
            select(
                Match.match_id, Match.date, Match.home_team_id, Match.away_team_id
            ).filter(Match.season.in_(seasons))
        ).all()
        match_map = {
            (match.date, match.home_team_id): match.match_id for match in matches
        }

        # Get opponent team IDs
        opponent_map = {
            t.name: t.team_id for t in session.execute(select(Team)).scalars()
        }

        # Insert shooting stats
        for _, row in df.iterrows():
            try:
                date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                is_home = row["Venue"] == "Home"
                opponent_name = row["Opponent"]
                opponent_team_id = opponent_map.get(opponent_name)

                if not opponent_team_id:
                    print(
                        f"Opponent {opponent_name} not found for {team_name} on {date}."
                    )
                    continue

                # Determine match_id
                match_key = (date, (team_id if is_home else opponent_team_id))
                match_id = match_map.get(match_key)

                if match_id is None:
                    print(
                        f"No match found for ({'Home' if is_home else 'Away'}) {team_name} vs {opponent_name} on {date}."
                    )
                    continue

                # Check for existing record
                existing_stat = session.execute(
                    select(MatchShootingStat).filter_by(
                        match_id=match_id, team_id=team_id
                    )
                ).scalar_one_or_none()

                if existing_stat:
                    # print(f"Shooting stat already exists for match_id={match_id}, team={team_name}.")
                    continue

                # Create new shooting stat record
                stat = MatchShootingStat(
                    match_id=match_id,
                    team_id=team_id,
                    round=row.get("Round"),
                    day=row.get("Day"),
                    venue=row.get("Venue"),
                    result=row.get("Result"),
                    gf=row.get("GF", None),
                    ga=row.get("GA", None),
                    opponent=row.get("Opponent"),
                    sh=row.get("Sh", None),
                    sot=row.get("SoT", None),
                    sot_percent=row.get("SoT%", None),
                    g_per_sh=row.get("G/Sh", None),
                    g_per_sot=row.get("G/SoT", None),
                    dist=row.get("Dist", None),
                    pk=row.get("PK", None),
                    pkatt=row.get("PKatt", None),
                    fk=row.get("FK", None),
                )
                session.add(stat)

            except Exception as e:
                print(f"Error processing row for {team_name} on {row['Date']}: {e}")
                continue

        session.commit()


if __name__ == "__main__":
    # Example usage
    df = pd.read_csv("../../data/shooting_stats_2013_Arsenal.csv")
    add_shooting_stats(df, team_name="Arsenal", season="2013-2014")
