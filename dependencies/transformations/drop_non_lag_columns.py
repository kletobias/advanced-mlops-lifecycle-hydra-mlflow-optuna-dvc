import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DropNonLagColumnsConfig:
    columns_to_drop: list[str]


def drop_non_lag_columns(df: pd.DataFrame, columns_to_drop: list[str]) -> pd.DataFrame:
    return df.drop(columns=columns_to_drop)
