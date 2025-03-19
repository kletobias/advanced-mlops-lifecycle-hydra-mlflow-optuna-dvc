import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DropDescriptionColumnsConfig:
    pattern: str
    inplace: bool


def drop_description_columns(
    df: pd.DataFrame,
    pattern: str,
    inplace: bool,
) -> pd.DataFrame:
    to_drop = df.filter(regex=f"{pattern}$").columns.tolist()
    logger.info("Done with core transformation: drop_description_columns")
    return pd.DataFrame(df.drop(columns=to_drop, inplace=inplace))
