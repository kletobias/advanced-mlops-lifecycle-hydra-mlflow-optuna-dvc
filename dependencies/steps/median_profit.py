# dependencies/steps/median_profit.py
import logging
from typing import TYPE_CHECKING

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.median_profit import MedianProfitConfig, median_profit

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@log_function_call
def step_median_profit(cfg: RootConfig) -> None:
    cfg_step = MedianProfitConfig(
        **cfg.transformations.median_profit.options_median_profit,
    )
    df: pd.DataFrame = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    df = median_profit(df, **cfg_step.__dict__)
    dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
