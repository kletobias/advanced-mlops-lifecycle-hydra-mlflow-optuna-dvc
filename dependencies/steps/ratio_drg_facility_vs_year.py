# dependencies/steps/ratio_drg_facility_vs_year.py
import logging
from typing import TYPE_CHECKING

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.ratio_drg_facility_vs_year import (
    RatioDrgFacilityVsYearConfig,
    ratio_drg_facility_vs_year,
)

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@log_function_call
def step_ratio_drg_facility_vs_year(cfg: RootConfig) -> None:
    cfg_step = RatioDrgFacilityVsYearConfig(
        **cfg.transformations.ratio_drg_facility_vs_year,
    )

    df: pd.DataFrame = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    df = ratio_drg_facility_vs_year(df, **cfg_step.__dict__)
    dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
