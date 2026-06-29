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
