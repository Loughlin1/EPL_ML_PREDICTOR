
TRAINING_DATA_START_SEASON = 2014
TRAINING_DATA_END_SEASON = 2023
SHOOTING_STATS_COLS = ["gf", "ga", "sh", "sot", "pk", "pkatt"]
rolling_home_cols = [f"{c}_rolling_h" for c in SHOOTING_STATS_COLS]
rolling_away_cols = [f"{c}_rolling_a" for c in SHOOTING_STATS_COLS]


FEATURES = [
    "home_team_encoded",
    "away_team_encoded",
    "week",
    "hour",
    "day_code",
    "venue_code",
    "season_encoded",
    "ppg_rolling_h",
    "ppg_rolling_a",
]
FEATURES.extend(rolling_home_cols)
FEATURES.extend(rolling_away_cols)
LABELS =  ["FTHG", "FTAG"]