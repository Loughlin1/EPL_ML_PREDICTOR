"""
Print feature importances for a trained season model.

For linear models shows normalised absolute coefficients.
For tree-based models shows feature_importances_.

Run from the backend directory:
    uv run python scripts/feature_importance.py
    uv run python scripts/feature_importance.py --season 2023-2024
"""

import argparse
import sys

sys.path.insert(0, ".")

from app.core.config import settings
from app.services.models.config import FEATURES
from app.services.models.save_load import load_model_for_season


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--season",
        default=settings.CURRENT_SEASON,
        help="Season to inspect (default: current season)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Show only the top N features (default: all)",
    )
    args = parser.parse_args()

    model = load_model_for_season(args.season)

    if not hasattr(model, "feature_importances"):
        print(f"Model for {args.season} is not a GoalPredictor — cannot extract importances.")
        sys.exit(1)

    importances = model.feature_importances(FEATURES)

    for label, pairs in importances.items():
        top = args.top or len(pairs)
        print(f"\n{'=' * 60}")
        print(f"Feature importances — {label} goals model ({args.season})")
        print(f"{'=' * 60}")
        print(f"{'Rank':<6}{'Feature':<35}{'Importance':>12}")
        print("-" * 55)
        for rank, (feature, score) in enumerate(pairs[:top], 1):
            bar = "█" * int(score * 40 / pairs[0][1]) if pairs[0][1] > 0 else ""
            print(f"{rank:<6}{feature:<35}{score:>10.4f}  {bar}")


if __name__ == "__main__":
    main()
