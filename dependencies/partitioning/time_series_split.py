import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def time_series_split(
    data: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = int(len(data) * train_ratio)
    train, test = data.iloc[:n], data[n:]
    return train, test
