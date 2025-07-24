
cols = ["GF", "GA", "Sh", "SoT", "PK", "PKatt"]
rolling_home_cols = [f"{c}_rolling_h" for c in cols]
rolling_away_cols = [f"{c}_rolling_a" for c in cols]


FEATURES = [
    "HomeTeamEncoded",
    "AwayTeamEncoded",
    "Wk",
    "hour",
    "day_code",
    "venue_code",
    "season_encoded",
    "PPG_rolling_h",
    "PPG_rolling_a",
]
FEATURES.extend(rolling_home_cols).extend(rolling_away_cols)