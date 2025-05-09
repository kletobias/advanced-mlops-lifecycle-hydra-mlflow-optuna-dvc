# dependencies/ingestion/ingest_data.py
import glob
import logging
import os
import subprocess
from dataclasses import dataclass

from dependencies.general.mkdir_if_not_exists import mkdir_
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata

logger = logging.getLogger(__name__)


@dataclass
class DownloadAndSaveDataConfig:
    dataset: str
    target_dir: str
    v0_csv_file_path: str
    v0_zip_file_path: str
    glob_pattern_csv_files: str
    glob_pattern_zip_files: str
    low_memory: bool
    output_metadata_file_path: str


def ingest_data(
    dataset: str,
    target_dir: str,
    v0_csv_file_path: str,
    v0_zip_file_path: str,
    glob_pattern_csv_files: str,
    glob_pattern_zip_files: str,
    low_memory: bool,
    output_metadata_file_path: str,
) -> None:
    """Downloads a dataset from Kaggle, extracts it,
    and renames the CSV file if needed.
    """
    mkdir_(target_dir)
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", dataset, "-p", target_dir],
            check=True,
        )
        logger.info("Successfully downloaded and saved the dataset.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to download and save the dataset.\n%s", e)
        raise RuntimeError from e

    zip_files = glob.glob(glob_pattern_zip_files)

    if not zip_files:
        msg = "No zip file found after download."
        raise FileNotFoundError(msg)
    downloaded_zip = zip_files[0]

    if os.path.abspath(downloaded_zip) != v0_zip_file_path:
        os.rename(downloaded_zip, v0_zip_file_path)
        logger.warning("Renamed ZIP file to %s", v0_zip_file_path)

    try:
        subprocess.run(["unzip", "-o", v0_zip_file_path, "-d", target_dir], check=True)
    except subprocess.CalledProcessError as e:
        logger.critical("Unzip failed: %s", e)
        raise RuntimeError from e

    csv_files = glob.glob(glob_pattern_csv_files)
    if not csv_files:
        logger.critical("No CSV file found after extraction")
        raise FileNotFoundError
    extracted_csv = csv_files[0]

    if os.path.abspath(extracted_csv) != v0_csv_file_path:
        os.rename(extracted_csv, v0_csv_file_path)

    os.remove(v0_zip_file_path)
    logger.info("Successfully removed ZIP file after extraction.")
    df = csv_to_dataframe(v0_csv_file_path, low_memory=low_memory)
    calculate_and_save_metadata(df, v0_csv_file_path, output_metadata_file_path)
