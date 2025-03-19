import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class RollingColumnsConfig:
    columns_to_transform: list[str]
    groupby_time_based_cols: list[str]
    drop: bool
    groupby_rolling_cols: list[str]
    rolling_str: str
    window: int
    shift_periods: int
    min_periods: int
    inplace: bool


def rolling_columns(
    df: pd.DataFrame,
    columns_to_transform: list[str],
    groupby_time_based_cols: list[str],
    drop: bool,
    groupby_rolling_cols: list[str],
    rolling_str: str,
    window: int,
    shift_periods: int,
    min_periods: int,
    inplace: bool,
) -> pd.DataFrame:
    groupby_time_based_cols = list(groupby_time_based_cols)
    groupby_rolling_cols = list(groupby_rolling_cols)
    drop = bool(drop)
    inplace = bool(inplace)

    df = df.sort_values(by=groupby_time_based_cols).reset_index(drop=drop)

    for col in columns_to_transform:
        df[f"{col}{rolling_str}{window}"] = df.groupby(groupby_rolling_cols)[
            col
        ].transform(
            lambda s: s.shift(shift_periods)
            .rolling(window=window, min_periods=min_periods)
            .mean()
        )

    rolling_cols = [f"{col}{rolling_str}{window}" for col in columns_to_transform]
    df = df.dropna(subset=rolling_cols, inplace=inplace)

    logger.info("Done with core transformation: rolling_columns")
    return df
