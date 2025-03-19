import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TotalMeanProfitConfig:
    total_mean_profit_col_name: str
    mean_profit_col_name: str
    discharges_col_name: str


def total_mean_profit(
    df: pd.DataFrame,
    total_mean_profit_col_name: str,
    mean_profit_col_name: str,
    discharges_col_name: str,
) -> pd.DataFrame:
    df[total_mean_profit_col_name] = df[mean_profit_col_name] * df[discharges_col_name]
    logger.info("Done with core transformation: total_mean_profit")

    return df
