# Makefile for EPL_ML_PREDICTOR

.PHONY: backend backend-dev frontend frontend-dev frontend-streamlit all help

help:
	@echo "Available targets:" && \
	grep -E '^[a-zA-Z0-9_.-]+:' Makefile | grep -v '^\.' | cut -d: -f1 | sort | uniq

tests:
	cd backend && PYTHONPATH=. uv run pytest tests/ --disable-warnings

backend:
	cd backend && export PYTHONPATH=$(pwd) && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000

backend-dev:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


frontend:
	cd frontend/react_ui && npm start

frontend-dev:
	cd frontend/react_ui && npm run dev

frontend-streamlit:
	cd frontend/streamlit && export PYTHONPATH=$(pwd) && uv run streamlit run Home.py


all: backend frontend-dev
