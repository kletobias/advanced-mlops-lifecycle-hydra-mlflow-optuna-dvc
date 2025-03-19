# dependencies/steps/mean_profit.py
import logging
from typing import TYPE_CHECKING

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.mean_profit import MeanProfitConfig, mean_profit

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@log_function_call
def step_mean_profit(cfg: RootConfig) -> None:
    cfg_step = MeanProfitConfig(**cfg.transformations.mean_profit.options_mean_profit)
    df: pd.DataFrame = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    df = mean_profit(df, **cfg_step.__dict__)
    dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
