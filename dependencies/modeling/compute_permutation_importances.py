from typing import Any
import pandas as pd
from sklearn.inspection import permutation_importance


def compute_permutation_importances(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
) -> dict[str, float]:
    perm_res = permutation_importance(model, X, y, random_state=random_state)
    return dict(zip(X.columns, perm_res.importances_mean))
