# dependencies/steps/total_mean_cost.py
import logging
from typing import TYPE_CHECKING

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.total_mean_cost import (
    TotalMeanCostConfig,
    total_mean_cost,
)

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@log_function_call
def step_total_mean_cost(cfg: RootConfig) -> None:
    cfg_step = TotalMeanCostConfig(
        **cfg.transformations.total_mean_cost.options_total_mean_cost,
    )
    df: pd.DataFrame = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    df = total_mean_cost(df, **cfg_step.__dict__)
    dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
