#!/bin/bash

# Ensure the script stops on error
set -e

cd backend

export PYTHONPATH=$(pwd)

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload