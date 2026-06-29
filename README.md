# EPL ML Predictor

A full-stack application that predicts English Premier League match outcomes using machine learning. Predictions are made per season using a linear regression model trained on historical match data, Elo ratings, rolling shooting stats, head-to-head records, and points-per-game features.

## Architecture

```
[React Frontend] <──> [FastAPI Backend] <──> [SQLite DB]
                              │
                    [ML Pipeline (scikit-learn)]
```

- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy (SQLite)
- **ML**: LinearRegression with StandardScaler, trained per season, persisted via joblib
- **Data**: Scraped from fbref.com and football-data.co.uk; cached in SQLite

## Directory Structure

```
EPL_ML_PREDICTOR/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint, global exception handler
│   │   ├── api/endpoints/           # Thin route handlers (fixtures, seasons, predict, etc.)
│   │   ├── core/                    # Config, paths
│   │   ├── db/                      # SQLAlchemy models, queries, migrations
│   │   ├── schemas/                 # Pydantic request/response models
│   │   └── services/                # All business logic
│   │       ├── data_processing/     # Feature engineering, data loading
│   │       ├── models/              # Train, predict, evaluate, summary
│   │       ├── utils/               # Matchweek, superbru points calculator
│   │       ├── web_scraping/        # fbref + football-data scrapers
│   │       ├── seasons_service.py   # Matchweek fetch + prediction cache logic
│   │       └── superbru_service.py  # Leaderboard cache logic
│   ├── scripts/
│   │   └── train_all_seasons.py     # CLI to train models for all or one season
│   └── tests/                       # pytest integration tests
│
├── frontend/
│   └── react_ui/
│       ├── src/
│       │   ├── App.jsx              # Season/matchweek state, data fetching
│       │   ├── api.js               # Axios API calls
│       │   └── components/          # MatchTable, MatchweekMenuBar, etc.
│       └── package.json
│
└── Makefile
```

## Getting Started

### Prerequisites

- Python 3.11+, [uv](https://github.com/astral-sh/uv)
- Node.js 18+

### Backend

```bash
cp backend/.env.example backend/.env  # fill in required vars
make backend-dev                       # starts FastAPI on :8000 with reload
```

### Frontend

```bash
make frontend-dev   # starts Vite dev server on :5173
```

### Train models

```bash
make train-all                          # train a model for every season in the DB
make train-season SEASON=2024-2025      # train for a single season
```

### Run tests

```bash
make tests
```

## API Endpoints

All routes are prefixed with `/api`.

### Seasons

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/seasons` | List all seasons available in the DB |
| GET | `/seasons/{season}/summary` | Season summary: superbru points, model performance |
| GET | `/seasons/{season}/matchweek` | Current/most recent matchweek number |
| GET | `/seasons/{season}/matchweek/{week}` | Match rows + week superbru points for one matchweek |

### Fixtures

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/fixtures` | All fixtures, optionally filtered by `?season=` and `?matchweek=` |
| GET | `/teams` | All teams in the DB |

### Model

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/predict` | Run prediction pipeline on provided fixtures |
| POST | `/train` | Trigger model training (optionally scoped to a season) |
| POST | `/evaluate` | Evaluate predictions against ground truth |
| GET | `/evaluate/validation` | Offline validation of the saved model |

### Superbru

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/superbru/points/top/global` | Top global leaderboard points, cached per season |

### Other

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/status` | Healthcheck |
| GET | `/content/model_explanation` | Model explanation content |

## ML Pipeline

Models are trained and stored per season (e.g. `model_2024-2025.joblib`). Training uses all data _before_ the target season, then generates and caches predictions for that season. Finished seasons are served entirely from the DB cache — no recomputation on request.

**Features used:** Elo ratings, rolling xG/shots, head-to-head record, points-per-game, home/away differentials.

**Target:** Full-time home goals (FTHG) and away goals (FTAG), from which result (W/D/L) and score string are derived.

## Caching Strategy

| Data | Cache location | Expiry |
|------|---------------|--------|
| Match predictions | `PredictionsCache` DB table | 24h (current season) / permanent (finished) |
| Season summary | `cache/season_summaries.json` | Permanent for finished seasons |
| Superbru leaderboard | `cache/superbru_leaderboard.json` | 90 days (current season) / permanent (finished) |

## Testing

```bash
make tests
```

23 integration tests cover all endpoints including 404 behaviour, field validation, NaN/Inf safety, season-scoped queries, and finished-season cache paths.
