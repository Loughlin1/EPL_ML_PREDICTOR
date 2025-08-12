import pandas as pd
from datetime import datetime


def get_current_matchweek(fixtures_df: pd.DataFrame) -> int:
    """
    Calculate the current matchweek based on today's date.

    fixtures_df should have at least these columns:
      - 'date': fixture date as string or datetime
      - 'week': integer matchweek number
    
    Returns:
        int: Current matchweek number
    """
    today = pd.to_datetime(datetime.today().date())
    fixtures_df['date'] = pd.to_datetime(fixtures_df['date'])

    past_fixtures = fixtures_df[fixtures_df['date'] <= today]

    if past_fixtures.empty:
        # No fixtures have occurred yet, return 1 as default
        return 1
    
    # Get max matchweek from fixtures up to today
    current_week = past_fixtures['week'].max()
    return int(current_week)

