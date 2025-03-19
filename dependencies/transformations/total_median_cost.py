import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TotalMedianCostConfig:
    total_median_cost_col_name: str
    median_cost_col_name: str
    discharges_col_name: str


def total_median_cost(
    df: pd.DataFrame,
    total_median_cost_col_name: str,
    median_cost_col_name: str,
    discharges_col_name: str,
) -> pd.DataFrame:
    df[total_median_cost_col_name] = df[median_cost_col_name] * df[discharges_col_name]
    logger.info("Done with core transformation: total_median_cost")

    return df
