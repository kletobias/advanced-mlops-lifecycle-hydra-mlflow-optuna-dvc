import logging

import mlflow
import optuna
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from dependencies.modeling.time_series_objective import time_series_objective

logger = logging.getLogger(__name__)


def run_optuna_study(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    features: list[str],
    tracking_uri: str,
    experiment_id: str,
    cv_splits: int,
    n_trials: int,
) -> optuna.Study:
    mlflow.set_tracking_uri(tracking_uri)
    logger.info("Set tracking uri to: %s", tracking_uri)

    mlflow.set_experiment(experiment_id)
    logger.info("mlflow.set_experiment: %s", experiment_id)

    cv = TimeSeriesSplit(n_splits=cv_splits)

    def wrapped_objective(trial: optuna.Trial) -> float:
        return time_series_objective(trial, X_train, y_train, features, cv)

    study = optuna.create_study(direction="minimize")
    study.optimize(wrapped_objective, n_trials=n_trials)
    return study
