#!/bin/bash

# Ensure the script stops on error
set -e

export PYTHONPATH=$(pwd)

# Activate your virtual environment if needed
source frontend/.venv/bin/activate

streamlit run frontend/Home.py