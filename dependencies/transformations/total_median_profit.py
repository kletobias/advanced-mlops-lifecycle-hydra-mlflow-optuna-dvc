import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TotalMedianProfitConfig:
    total_median_profit_col_name: str
    median_profit_col_name: str
    discharges_col_name: str


def total_median_profit(
    df: pd.DataFrame,
    total_median_profit_col_name: str,
    median_profit_col_name: str,
    discharges_col_name: str,
) -> pd.DataFrame:
    df[total_median_profit_col_name] = (
        df[median_profit_col_name] * df[discharges_col_name]
    )
    logger.info("Done with core transformation: total_median_profit")
    assert total_median_profit_col_name in df.columns.tolist(), "total_median_profit not in columns"

    return df
