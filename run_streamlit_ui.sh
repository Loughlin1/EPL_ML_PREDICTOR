#!/bin/bash

# Ensure the script stops on error
set -e

cd frontend/streamlit_ui

export PYTHONPATH=$(pwd)

uv run streamlit run Home.py