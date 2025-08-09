#!/bin/bash

# Ensure the script stops on error
set -e

cd backend

# Set the PYTHONPATH to the root of the repo
export PYTHONPATH=$(pwd)

# Activate your virtual environment if needed
source .venv/bin/activate

python -m app.services.web_scraping.players.fifa_ratings
