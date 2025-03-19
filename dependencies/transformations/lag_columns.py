import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class LagColumnsConfig:
    columns_to_transform: list[str]
    groupby_time_based_cols: list[str]
    drop: bool
    groupby_lag_cols: list[str]
    lag1_suffix: str
    shift_periods: int


def lag_columns(
    df: pd.DataFrame,
    columns_to_transform: list[str],
    groupby_time_based_cols: list[str],
    drop: bool,
    groupby_lag_cols: list[str],
    lag1_suffix: str,
    shift_periods: int,
) -> pd.DataFrame:
    groupby_time_based_cols = list(groupby_time_based_cols)
    groupby_lag_cols = list(groupby_lag_cols)
    drop = bool(drop)

    df = df.sort_values(by=groupby_time_based_cols).reset_index(drop=drop)

    for col in columns_to_transform:
        df[f"{col}{lag1_suffix}"] = df.groupby(groupby_lag_cols)[col].shift(
            shift_periods
        )

    logger.info("Done with core transformation: lag_columns")
    return df
