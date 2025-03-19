import logging
import os
from math import sqrt

import mlflow
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from dependencies.general.mkdir_if_not_exists import mkdir_
from dependencies.modeling.compute_permutation_importances import (
    compute_permutation_importances,
)

logger = logging.getLogger(__name__)


def train_final_model_and_log(
    study: optuna.Study,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    features: list[str],
    tracking_uri: str,
    experiment_id: str,
    top_n_importances: int,
    final_model_artifact_sub_dir: str,
    feature_importances_artifact_sub_dir: str,
    feature_importances_csv_file_path: str,
):
    mlflow.set_tracking_uri(tracking_uri)
    logger.info("Set tracking uri to: %s", tracking_uri)

    mlflow.set_experiment(experiment_id)
    logger.info("mlflow.set_experiment: %s", experiment_id)

    # Retrieve best hyperparameters from Optuna study
    best_params = study.best_params
    final_model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
    final_model.fit(X_train[features], y_train)

    # Make predictions on validation set
    y_pred_val = final_model.predict(X_val[features])
    val_rmse = sqrt(mean_squared_error(y_val, y_pred_val))
    val_mae = mean_absolute_error(y_val, y_pred_val)

    # Extract RF feature importances as a NumPy array
    rf_importances_array = final_model.feature_importances_

    # Compute permutation importances
    permutation_importances_dict = compute_permutation_importances(
        final_model,
        X_train[features],
        y_train,
    )

    # Convert RF importances to a dict keyed by feature name
    rf_importances_dict = dict(zip(features, rf_importances_array))

    with mlflow.start_run(run_name="final_model"):
        # Log main metrics
        mlflow.log_metric("val_rmse", val_rmse)
        mlflow.log_metric("val_mae", val_mae)

        # Log model hyperparameters
        for k, v in best_params.items():
            mlflow.log_param(k, v)

        # Log the trained model
        mlflow.sklearn.log_model(
            final_model,
            artifact_path=final_model_artifact_sub_dir,
        )

        # Sort features by absolute permutation importance
        sorted_permutation_feats = sorted(
            permutation_importances_dict,
            key=lambda f: abs(permutation_importances_dict[f]),
            reverse=True,
        )

        # Sort features by absolute RF feature importance
        sorted_rf_feats = sorted(
            rf_importances_dict,
            key=lambda f: abs(rf_importances_dict[f]),
            reverse=True,
        )

        # Log top_n_importances for permutation importances
        for feat in sorted_permutation_feats[:top_n_importances]:
            mlflow.log_metric(f"perm_imp_{feat}", permutation_importances_dict[feat])

        # Log top_n_importances for the RF feature_importances_
        for feat in sorted_rf_feats[:top_n_importances]:
            mlflow.log_metric(f"rf_importance_{feat}", rf_importances_dict[feat])

        # Create a DataFrame for permutation importances and save
        df_perm_imp = pd.DataFrame(
            [
                {"feature": f, "importance": permutation_importances_dict[f]}
                for f in sorted_permutation_feats
            ],
        )

        df_rf_imp = pd.DataFrame(
            [
                {"feature": f, "importance": rf_importances_dict[f]}
                for f in sorted_rf_feats
            ],
        )
        rf_importances_csv_file_path = feature_importances_csv_file_path.replace(
            ".csv",
            "_rf.csv",
        )

        # Ensure directory exists
        mkdir_(os.path.dirname(feature_importances_csv_file_path))

        # Save permutation importances to CSV
        df_perm_imp.to_csv(feature_importances_csv_file_path, index=False)
        mlflow.log_artifact(
            feature_importances_csv_file_path,
            artifact_path=feature_importances_artifact_sub_dir,
        )

        df_rf_imp.to_csv(rf_importances_csv_file_path, index=False)
        mlflow.log_artifact(
            rf_importances_csv_file_path,
            artifact_path=feature_importances_artifact_sub_dir,
        )

    return final_model
