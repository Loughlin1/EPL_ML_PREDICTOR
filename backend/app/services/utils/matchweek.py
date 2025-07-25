import pandas as pd
from datetime import datetime


def get_current_matchweek(fixtures_df: pd.DataFrame) -> int:
    """
    Calculate the current matchweek based on today's date.

    fixtures_df should have at least these columns:
      - 'Date': fixture date as string or datetime
      - 'Matchweek': integer matchweek number
    
    Returns:
        int: Current matchweek number
    """
    today = pd.to_datetime(datetime.today().date())
    fixtures_df['Date'] = pd.to_datetime(fixtures_df['Date'])

    past_fixtures = fixtures_df[fixtures_df['Date'] <= today]

    if past_fixtures.empty:
        # No fixtures have occurred yet, return 1 as default
        return 1
    
    # Get max matchweek from fixtures up to today
    current_week = past_fixtures['Wk'].max()
    return int(current_week)

