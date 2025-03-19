import logging

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.ingestion.download_dataset_kaggle_api import (
    download_dataset_kaggle_api,
)
from dependencies.ingestion.extract_zip import extract_zip
from dependencies.ingestion.rename_csv_and_cleanup import rename_csv_and_cleanup
from dependencies.ingestion.rename_downloaded_zip import rename_downloaded_zip
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata


@log_function_call
def step_download_and_save_data(cfg: RootConfig) -> None:
    download_dataset_kaggle_api(cfg)
    zip_path = rename_downloaded_zip(cfg)
    extract_zip(zip_path, cfg)
    rename_csv_and_cleanup(cfg)
    df = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
    calculate_and_save_metadata(df, **cfg.utility_functions.calculate_and_save_metadata)
