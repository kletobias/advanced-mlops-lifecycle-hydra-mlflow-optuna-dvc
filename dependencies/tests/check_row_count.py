# dependencies/tests/check_row_count.py
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import pandera.errors as pe

logger = logging.getLogger(__name__)


@dataclass
class CheckRowCountConfig:
    row_count: int


def check_row_count(
    df: pd.DataFrame,
    row_count: int,
) -> pd.DataFrame:
    n = df.shape[0]

    if n != row_count:
        logger.error("Row count mismatch: %s != %s", n, row_count)
        raise pe.SchemaError(
            schema=None,
            data=df,
            message=f"Row count mismatch: Excpected {row_count}, got {n}",
        )

    return df
