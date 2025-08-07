#!/bin/bash

# Exit on first error
set -e

echo "📦 Installing test dependencies (if needed)..."
pip install -r requirements.txt > /dev/null 2>&1 || true

echo "🧪 Running tests with PYTHONPATH=."
PYTHONPATH=. uv run pytest tests/ --disable-warnings

echo "✅ All tests passed!"