import logging
from typing import Literal
import pandas as pd

logger = logging.getLogger(__name__)


def df_merge(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    on: str,
    how: Literal["left", "right", "inner", "outer", "cross"],
) -> pd.DataFrame:
    logger.info("Successfully merged df1, and df2 on: %s, how: %s", on, how)
    return pd.merge(df1, df2, on=on, how=how)
