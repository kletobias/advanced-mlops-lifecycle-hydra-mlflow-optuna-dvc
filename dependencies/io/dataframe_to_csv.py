import logging
import os

import pandas as pd

from dependencies.general.mkdir_if_not_exists import mkdir_

logger = logging.getLogger(__name__)


def dataframe_to_csv(
    df: pd.DataFrame,
    output_file_path_csv: str,
    include_index: bool,
) -> None:
    mkdir_(os.path.dirname(output_file_path_csv))
    logger.debug("Output CSV file path: %s", output_file_path_csv)
    df.to_csv(output_file_path_csv, index=include_index)
    logger.info("Exported df to csv using filepath: %s", output_file_path_csv)
