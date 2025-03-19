# dependencies/steps/agg_severities.py
# 7
import logging
from typing import TYPE_CHECKING

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.agg_severities import (
    AggSeveritiesConfig,
    agg_severities,
)

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@log_function_call
def step_agg_severities(cfg: RootConfig) -> None:
    """Reads data via csv_to_dataframe, applies the agg_severities transformation,
    writes out the results, and calculates/saves metadata.
    """
    cfg_step = AggSeveritiesConfig(**cfg.transformations.agg_severities)

    df: pd.DataFrame = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    df = agg_severities(df, **cfg_step.__dict__)
    dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
