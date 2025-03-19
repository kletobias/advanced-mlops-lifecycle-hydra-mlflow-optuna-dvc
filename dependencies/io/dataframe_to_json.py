import logging

logger = logging.getLogger(__name__)
import os

import pandas as pd


def dataframe_to_json(
    df: pd.DataFrame,
    json_file_path: str,
    include_index: bool = False,
) -> None:
    if not os.path.isdir(os.path.dirname(json_file_path)):
        mkdir(os.path.dirname(json_file_path))
    df.to_json(json_file_path, orient="records", index=include_index)
    logger.info("Exported df: %s, to json_file_path: %s", df, json_file_path)
