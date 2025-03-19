import logging

logger = logging.getLogger(__name__)

import pandas as pd


def dataframe_get_column_dtypes(df: pd.DataFrame) -> tuple[dict[str, str], str]:
    logger.info("Returning column data types, output file name.")
    return {col: str(df[col].dtype) for col in df.columns.to_list()}
