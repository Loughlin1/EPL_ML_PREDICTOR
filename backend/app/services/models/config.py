TRAINING_DATA_START_SEASON = 2014       # 2014-2015
TRAINING_DATA_END_SEASON = 2024         # 2024-2025
SHOOTING_STATS_COLS = ["gf", "ga", "sh", "sot", "sot_percent", "g_per_sh", "g_per_sot", "pk", "pkatt"]
SH_ROLLING_HOME_COLS = [f"{c}_rolling_h" for c in SHOOTING_STATS_COLS]
SH_ROLLING_AWAY_COLS = [f"{c}_rolling_a" for c in SHOOTING_STATS_COLS]
SH_ROLLING_COLS = SH_ROLLING_HOME_COLS + SH_ROLLING_AWAY_COLS

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
    "pos_last_season_h",
    "pos_last_season_a",
    "elo_h",
    "elo_a",
    "h2h_avg_goals_h",
    "h2h_avg_goals_a",
]
FEATURES.extend(SH_ROLLING_HOME_COLS)
FEATURES.extend(SH_ROLLING_AWAY_COLS)
LABELS = ["FTHG", "FTAG"]
