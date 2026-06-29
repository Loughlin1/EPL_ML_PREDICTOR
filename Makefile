# Makefile for EPL_ML_PREDICTOR

.PHONY: backend backend-dev frontend frontend-dev all help

help:
	@echo "Available targets:" && \
	grep -E '^[a-zA-Z0-9_.-]+:' Makefile | grep -v '^\.' | cut -d: -f1 | sort | uniq

tests:
	cd backend && PYTHONPATH=. uv run pytest tests/ --disable-warnings

backend:
	cd backend && export PYTHONPATH=$(pwd) && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

backend-dev:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


frontend:
	cd frontend/react_ui && npm start

frontend-dev:
	cd frontend/react_ui && npm run dev

all: backend frontend-dev
