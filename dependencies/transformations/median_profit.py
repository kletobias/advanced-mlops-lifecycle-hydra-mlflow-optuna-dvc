import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MedianProfitConfig:
    median_profit_col_name: str
    median_charge_col_name: str
    median_cost_col_name: str


def median_profit(
    df: pd.DataFrame,
    median_profit_col_name: str,
    median_charge_col_name: str,
    median_cost_col_name: str,
) -> pd.DataFrame:
    df[median_profit_col_name] = df[median_charge_col_name] - df[median_cost_col_name]
    logger.info("Done with core transformation: median_profit")
    return df
