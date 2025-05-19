# dependencies/tests/check_row_count.py
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import pandera.errors as pe

logger = logging.getLogger(__name__)


@dataclass
class CheckRowCountConfig:
    row_count: int | list[int] = 0  # int or two-element list
    data_version_output: str = ""  # e.g. "v0" … "v13"


def check_row_count(
    df: pd.DataFrame,
    row_count: int | list[int],
    data_version_output: str = "",
) -> pd.DataFrame:
    n = df.shape[0]
    data_version_output_int = int(data_version_output[1:])
    if not data_version_output_int:
        logger.error("data_version_output must be a string starting with 'v'")
        raise ValueError

    if isinstance(row_count, int) and (row_count > 0 and n != row_count):
        logger.error("Row count mismatch: %s != %s", n, row_count)
        raise pe.SchemaError(schema=None, data=df)

    if isinstance(row_count, list) and len(row_count) != 2:
        logger.error("row_count list must contain exactly two integers")
        raise ValueError

    if data_version_output:
        expected = row_count[0] if int(data_version_output_int) < 8 else row_count[1]
        if n != expected:
            logger.error("Row count mismatch: %s != %s", n, expected)
            raise pe.SchemaError(schema=None, data=df)

    return df
