# Makefile for EPL_ML_PREDICTOR

.PHONY: help backend backend-dev frontend frontend-dev dev tests lint \
        train-all train-season

# ──────────────────────────────────────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
	  /^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 } \
	  /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

# ──────────────────────────────────────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────────────────────────────────────

##@ Development

backend-dev: ## Start FastAPI with hot-reload on :8000
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Start Vite dev server on :5173
	cd frontend/react_ui && npm run dev

dev: ## Start backend and frontend dev servers (requires two terminals)
	@echo "Run 'make backend-dev' and 'make frontend-dev' in separate terminals."

# ──────────────────────────────────────────────────────────────────────────────
# Production
# ──────────────────────────────────────────────────────────────────────────────

##@ Production

backend: ## Start FastAPI production server on :8000
	cd backend && export PYTHONPATH=$(PWD) && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

frontend: ## Build and preview the React frontend
	cd frontend/react_ui && npm run build && npm run preview

# ──────────────────────────────────────────────────────────────────────────────
# Testing & linting
# ──────────────────────────────────────────────────────────────────────────────

##@ Quality

tests: ## Run the backend test suite
	cd backend && PYTHONPATH=. uv run pytest tests/ --disable-warnings -v

lint: ## Lint and format backend with ruff
	cd backend && uv run ruff check . --fix && uv run ruff format .

# ──────────────────────────────────────────────────────────────────────────────
# Model training
# ──────────────────────────────────────────────────────────────────────────────

##@ Model training

train-all: ## Train a model for every season in the database
	cd backend && PYTHONPATH=. uv run python scripts/train_all_seasons.py

train-season: ## Train for a single season  e.g. make train-season SEASON=2024-2025
	@test -n "$(SEASON)" || (echo "Error: SEASON is required. Usage: make train-season SEASON=2024-2025" && exit 1)
	cd backend && PYTHONPATH=. uv run python scripts/train_all_seasons.py --season $(SEASON)
