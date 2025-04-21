import logging
from dataclasses import dataclass

import pandas as pd
from slugify import slugify

logger = logging.getLogger(__name__)


@dataclass
class SanitizeColumnNamesConfig:
    pass


def sanitize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with sanitized column names."""
    sanitized_columns = [slugify(col).replace("-", "_") for col in df.columns]
    df.columns = sanitized_columns
    logger.info("Column names sanitized")
    return df
