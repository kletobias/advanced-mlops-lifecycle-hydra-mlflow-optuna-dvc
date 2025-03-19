import logging

import mlflow
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_validate

logger = logging.getLogger(__name__)


def time_series_objective(
    trial: optuna.Trial,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    features: list[str],
    cv: TimeSeriesSplit,
) -> float:
    scoring = {"rmse": "neg_root_mean_squared_error", "r2": "r2"}

    n_estimators = trial.suggest_int("n_estimators", 100, 1000, step=10)
    max_depth = trial.suggest_int("max_depth", 5, 50, step=5)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 50)
    min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 50)
    min_weight_fraction_leaf = trial.suggest_float("min_weight_fraction_leaf", 0.1, 0.5)
    max_features = trial.suggest_float("max_features", 0.1, 1.0)
    max_leaf_nodes = trial.suggest_int("max_leaf_nodes", 5, 500, step=10)
    min_impurity_decrease = trial.suggest_float("min_impurity_decrease", 0.0, 0.1)
    ccp_alpha = trial.suggest_float("ccp_alpha", 0.02, 0.1)
    max_samples = trial.suggest_int("max_samples", 10, 500, step=10)

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        min_weight_fraction_leaf=min_weight_fraction_leaf,
        max_features=max_features,
        max_leaf_nodes=max_leaf_nodes,
        min_impurity_decrease=min_impurity_decrease,
        bootstrap=True,
        oob_score=True,
        n_jobs=-1,
        random_state=42,
        ccp_alpha=ccp_alpha,
        max_samples=max_samples,
    )

    results = cross_validate(
        model,
        X_train[features],
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
    )
    rmse = -np.mean(results["test_rmse"])
    r2 = np.mean(results["test_r2"])

    with mlflow.start_run(nested=True):
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("min_samples_split", min_samples_split)
        mlflow.log_param("min_samples_leaf", min_samples_leaf)
        mlflow.log_param("min_weight_fraction_leaf", min_weight_fraction_leaf)
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("max_leaf_nodes", max_leaf_nodes)
        mlflow.log_param("min_impurity_decrease", min_impurity_decrease)
        mlflow.log_param("ccp_alpha", ccp_alpha)
        mlflow.log_param("max_samples", max_samples)

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

    return rmse
