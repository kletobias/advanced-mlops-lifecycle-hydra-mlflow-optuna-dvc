"""Reads a CSV file, and returns a pd.DataFrame."""

# dependencies/io/csv_to_dataframe.py
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def csv_to_dataframe(
    csv_file_path: str,
    low_memory: bool,
) -> pd.DataFrame:
    """Reads a CSV file and returns a pd.DataFrame."""
    df = pd.read_csv(csv_file_path, low_memory=low_memory)
    logger.info("Read %s, created df", csv_file_path)
    return df
