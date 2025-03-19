# dependencies/logging_utils/calculate_and_log_importances_as_artifact.py
import logging
from typing import Any
import mlflow
import pandas as pd
from dependencies.modeling.compute_permutation_importances import (
    compute_permutation_importances,
)
import os

logger = logging.getLogger(__name__)


def calculate_and_log_importances_as_artifact(
    importances_filename: str, model: Any, X: pd.DataFrame, y: pd.Series
) -> None:
    perm_dict = compute_permutation_importances(model, X, y)
    sorted_perm = sorted(perm_dict, key=lambda f: abs(perm_dict[f]), reverse=True)
    pd.DataFrame(
        [{"feature": f, "importances": perm_dict[f]} for f in sorted_perm]
    ).to_csv(importances_filename, index=False)
    mlflow.log_artifact(importances_filename, artifact_path="importances")
    if os.path.exists(importances_filename):
        os.remove(importances_filename)
        logger.info("Removed %s project root directory", importances_filename)
