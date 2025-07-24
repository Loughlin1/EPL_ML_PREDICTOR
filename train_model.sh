#!/bin/bash

# Ensure the script stops on error
set -e

# Set the PYTHONPATH to the root of the repo
export PYTHONPATH=$(pwd)

# Activate your virtual environment if needed
source backend/.venv/bin/activate

python backend/models/train.py
