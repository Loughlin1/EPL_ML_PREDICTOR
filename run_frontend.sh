#!/bin/bash

# Ensure the script stops on error
set -e

cd frontend

export PYTHONPATH=$(pwd)

uv run streamlit run Home.py