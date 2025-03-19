import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MeanProfitConfig:
    mean_profit_col_name: str
    mean_charge_col_name: str
    mean_cost_col_name: str


def mean_profit(
    df: pd.DataFrame,
    mean_profit_col_name: str,
    mean_charge_col_name: str,
    mean_cost_col_name: str,
) -> pd.DataFrame:
    df[mean_profit_col_name] = df[mean_charge_col_name] - df[mean_cost_col_name]
    logger.info("Done with core transformation: mean_profit")
    return df
