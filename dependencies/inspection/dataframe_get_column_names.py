import logging

logger = logging.getLogger(__name__)

import pandas as pd


def dataframe_get_column_names(df: pd.DataFrame) -> tuple[dict[int, str], str]:
    logger.info("Returning: column names dictionary, output file name")
    return dict(enumerate(df.columns.to_list())), "column_names.json"
