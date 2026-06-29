from __future__ import annotations

import numpy as np


class GoalPredictor:
    """
    Uniform interface over any sklearn-compatible goal-scoring model.

    Pass a single multi-output estimator, or separate home/away estimators:
        GoalPredictor(LinearRegression())                      # multi-output
        GoalPredictor(XGBRegressor(), XGBRegressor())          # two single-output
    """

    def __init__(self, home_model, away_model=None):
        self.home_model = home_model
        self.away_model = away_model

    def fit(self, X, y):
        if self.away_model is None:
            self.home_model.fit(X, y)
        else:
            self.home_model.fit(X, y.iloc[:, 0])
            self.away_model.fit(X, y.iloc[:, 1])
        return self

    def predict(self, X) -> np.ndarray:
        """Return shape (n, 2) array of [[home_goals, away_goals], ...]."""
        if self.away_model is None:
            return np.round(self.home_model.predict(X)).astype(int)
        return np.column_stack([
            np.round(self.home_model.predict(X)).astype(int),
            np.round(self.away_model.predict(X)).astype(int),
        ])

    def feature_importances(self, feature_names: list[str]) -> dict[str, list]:
        """
        Return feature importances (or coefficients) for home and away models.

        For tree-based models uses feature_importances_; for linear models uses
        the absolute value of coefficients. Returns a dict with keys 'home' and
        optionally 'away', each a list of (feature, importance) tuples sorted
        descending by importance.
        """
        def _extract(model, label: str):
            if hasattr(model, "feature_importances_"):
                scores = model.feature_importances_
            elif hasattr(model, "coef_"):
                coef = model.coef_
                # Multi-output linear: coef_ shape is (n_outputs, n_features)
                scores = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)
            else:
                raise ValueError(f"{label} model has no feature_importances_ or coef_")
            pairs = sorted(zip(feature_names, scores.tolist()), key=lambda x: x[1], reverse=True)
            return pairs

        result = {"home": _extract(self.home_model, "home")}
        if self.away_model is not None:
            result["away"] = _extract(self.away_model, "away")
        return result
