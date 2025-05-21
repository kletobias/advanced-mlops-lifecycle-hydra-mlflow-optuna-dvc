# dependencies/modeling/rf_optuna_trial.py
import logging
import os
from dataclasses import dataclass
from math import sqrt
from typing import Any

import mlflow
import numpy as np
import optuna
import pandas as pd
from mlflow.data.pandas_dataset import PandasDataset
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit, cross_validate

from dependencies.logging_utils.calculate_and_log_importances_as_artifact import (
    calculate_and_log_importances_as_artifact,
)
from dependencies.modeling.optuna_random_search_util import optuna_random_search_util
from dependencies.modeling.rf_sklearn_instantiate_rfr_class import (
    rf_sklearn_instantiate_rfr_class,
)
from dependencies.modeling.validate_parallelism import validate_parallelism

logger = logging.getLogger(__name__)


@dataclass
class RfOptunaTrialConfig:
    target_col: str
    year_col: str
    train_range: tuple[int, int]
    val_range: tuple[int, int]
    test_range: tuple[int, int]
    experiment_name: str
    cv_splits: int
    n_trials: int
    top_n_importances: int
    permutation_importances_filename: str
    randomforest_importances_filename: str
    hyperparameters: dict
    rfr_options: dict
    n_jobs_study: int
    n_jobs_cv: int
    n_jobs_final_model: int
    random_state: int
    model_tags: Any


def rf_optuna_trial(
    df: pd.DataFrame,
    target_col: str,
    year_col: str,
    train_range: tuple[int, int],
    val_range: tuple[int, int],
    test_range: tuple[int, int],
    experiment_name: str,  # only the experiment name
    cv_splits: int,
    n_trials: int,
    top_n_importances: int,
    permutation_importances_filename: str,
    randomforest_importances_filename: str,
    hyperparameters: dict,
    rfr_options: dict,
    n_jobs_study: int,
    n_jobs_cv: int,
    n_jobs_final_model: int,
    random_state: int,
    model_tags: Any,
) -> None:
    """Minimal version using MLflow's default local './mlruns' directory.
    We do not use any output/experiment paths from the config.
    """
    validate_parallelism(n_jobs_cv=n_jobs_cv, n_jobs_study=n_jobs_study)
    logger.info("Starting rf_optuna_trial with %i trials to run", n_trials)

    # Always use the default local mlruns folder
    mlflow.set_tracking_uri("file:./mlruns")

    # Create or set experiment by name
    existing = mlflow.get_experiment_by_name(experiment_name)
    if existing is None:
        experiment_id = mlflow.create_experiment(experiment_name)

    if "index" in df.columns:
        feature_cols = [c for c in df.columns if c not in [target_col, "index"]]
    else:
        feature_cols = [c for c in df.columns if c != target_col]

    dataset: PandasDataset = mlflow.data.from_pandas(
        df, source=model_tags.get("input_file_path", "")
    )

    def partition_data() -> dict[str, pd.DataFrame]:
        df_train = df[
            (df[year_col] >= train_range[0]) & (df[year_col] <= train_range[1])
        ]
        df_val = df[(df[year_col] >= val_range[0]) & (df[year_col] <= val_range[1])]
        df_test = df[(df[year_col] >= test_range[0]) & (df[year_col] <= test_range[1])]

        return {
            "X_train": df_train[feature_cols],
            "y_train": df_train[target_col],
            "X_val": df_val[feature_cols],
            "y_val": df_val[target_col],
            "X_test": df_test[feature_cols],
            "y_test": df_test[target_col],
        }

    data_part = partition_data()
    X_train, y_train = data_part["X_train"], data_part["y_train"]
    X_val, y_val = data_part["X_val"], data_part["y_val"]
    X_test, y_test = data_part["X_test"], data_part["y_test"]

    X_train_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(X_train))
    y_train_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(y_train))
    X_val_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(X_val))
    y_val_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(y_val))
    X_test_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(X_test))
    y_test_dataset: PandasDataset = mlflow.data.from_pandas(pd.DataFrame(y_test))

    def objective(trial: optuna.Trial) -> float:
        # sample hyperparams from config
        final_params = optuna_random_search_util(trial, hyperparameters)
        # instantiate with rfr_options
        model = rf_sklearn_instantiate_rfr_class(final_params, rfr_options)

        cv_obj = TimeSeriesSplit(n_splits=cv_splits)
        scoring = {"rmse": "neg_root_mean_squared_error", "r2": "r2"}
        results = cross_validate(
            model,
            X_train,
            y_train,
            cv=cv_obj,
            scoring=scoring,
            n_jobs=n_jobs_cv,
        )

        rmse = -np.mean(results["test_rmse"])
        r2 = np.mean(results["test_r2"])

        with mlflow.start_run(
            experiment_id=experiment_id,
            run_name="training",
            tags=model_tags,
            nested=True,
        ):
            mlflow.log_input(dataset, context="training", tags=model_tags)
            mlflow.log_input(
                X_train_dataset,
                context="training",
                tags=model_tags.update({"split": "X_train"}),
            )
            mlflow.log_input(
                y_train_dataset,
                context="training",
                tags=model_tags.update({"split": "y_train"}),
            )
            mlflow.log_param("training", "True")
            mlflow.log_param("cv_score", "True")
            mlflow.log_param("data_partition", "train")
            mlflow.log_params(results)
            mlflow.log_params(final_params)
            mlflow.log_metrics({"rmse": np.round(rmse, 0), "r2": r2})

        completed = [
            t for t in trial.study.trials if t.state == optuna.trial.TrialState.COMPLETE
        ]
        if completed:
            best_val = trial.study.best_value or float("inf")
            logger.info(
                "Trial %d => RMSE=%.3f R2=%.3f (Best so far=%.3f)",
                trial.number,
                rmse,
                r2,
                min(best_val, rmse),
            )
        else:
            logger.info(
                "Trial %d => RMSE=%.3f R2=%.3f (No best yet)",
                trial.number,
                rmse,
                r2,
            )

        return rmse

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs_study)

    # Final Model
    if not any(t.state == optuna.trial.TrialState.COMPLETE for t in study.trials):
        logger.warning("No completed trials found, skipping final model")
        return

    logger.info("Training final model on best_params")
    best_params = study.best_params
    final_model = RandomForestRegressor(
        **best_params,
        random_state=random_state,
        n_jobs=n_jobs_final_model,
    )
    final_model.fit(X_train, y_train)

    y_pred_val = final_model.predict(X_val)
    val_rmse = sqrt(mean_squared_error(y_val, y_pred_val))
    val_mae = mean_absolute_error(y_val, y_pred_val)

    with mlflow.start_run(
        run_name="final_model",
        experiment_id=experiment_id,
        nested=True,
        tags=model_tags,
    ):
        mlflow.log_input(dataset, context="validation", tags=model_tags)
        mlflow.log_input(
            X_val_dataset,
            context="validation",
            tags=model_tags.update({"split": "X_val"}),
        )
        mlflow.log_input(
            y_val_dataset,
            context="validation",
            tags=model_tags.update({"split": "y_val"}),
        )
        mlflow.log_param("validation", "True")
        mlflow.log_param("data_partition", "val")
        mlflow.log_metric("rmse", val_rmse)
        mlflow.log_metric("mae", val_mae)
        mlflow.log_metrics(
            {"val_rmse": np.round(val_rmse, 0), "val_mae": np.round(val_mae, 0)}
        )
        mlflow.log_params(best_params)
        mlflow.log_param("y_pred_val", y_pred_val)
        mlflow.sklearn.log_model(final_model, artifact_path="model")

        # Permutation importances
        calculate_and_log_importances_as_artifact(
            permutation_importances_filename,
            final_model,
            X_train,
            y_train,
        )

        # RandomForest importances
        rf_import = dict(zip(feature_cols, final_model.feature_importances_))
        sorted_rf = sorted(rf_import, key=lambda f: abs(rf_import[f]), reverse=True)

        for feat in sorted_rf[:top_n_importances]:
            mlflow.log_metric(f"rf_importance_{feat}", rf_import[feat])

        pd.DataFrame(
            [{"feature": f, "importance": rf_import[f]} for f in sorted_rf],
        ).to_csv(randomforest_importances_filename, index=False)
        mlflow.log_artifact(
            randomforest_importances_filename,
            artifact_path="importances",
        )
        if os.path.exists(randomforest_importances_filename):
            os.remove(randomforest_importances_filename)
            logger.info(
                "Removed %s project root directory",
                randomforest_importances_filename,
            )

        y_pred_test = final_model.predict(X_test)
        test_rmse = sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)
        with mlflow.start_run(
            experiment_id=experiment_id,
            run_name="final_model_predict_test",
            tags=model_tags,
            nested=True,
        ):
            mlflow.log_metrics(
                {"test_rmse": np.round(test_rmse, 0), "test_mae": np.round(test_mae, 0)}
            )
            mlflow.log_input(dataset, context="test", tags=model_tags)
            mlflow.log_input(
                X_test_dataset,
                context="test",
                tags=model_tags.update({"split": "X_test"}),
            )
            mlflow.log_input(
                y_test_dataset,
                context="test",
                tags=model_tags.update({"split": "y_test"}),
            )
            mlflow.log_metric("rmse", test_rmse)
            mlflow.log_metric("mae", test_mae)
            mlflow.log_param("test", "True")
            mlflow.log_param("data_partition", "test")

    logger.info("Done with rf_optuna_trial. All outputs in ./mlruns/")
