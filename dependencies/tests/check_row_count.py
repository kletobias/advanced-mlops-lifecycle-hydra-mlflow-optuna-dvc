# dependencies/tests/check_row_count.py
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd
import pandera.errors as pe

logger = logging.getLogger(__name__)


@dataclass
class CheckRowCountConfig:
    row_count: list[int] = field(default_factory=list)
    data_version_output: str = field(default_factory=str)


def check_row_count(
    df: pd.DataFrame,
    row_count: list[int],
    data_version_output: str,
) -> pd.DataFrame:
    n = df.shape[0]

    try:
        data_version_output_int = int(data_version_output[1:])
    except (TypeError, ValueError):
        logger.error(
            "Failed to convert data_version_output to int: %s", data_version_output
        )
        raise ValueError

    if len(row_count) != 2:
        logger.error("row_count list must contain exactly two integers")
        raise ValueError
    expected = row_count[0] if data_version_output_int < 8 else row_count[1]
    if n != expected:
        logger.error("Row count mismatch: %s != %s", n, expected)
        raise pe.SchemaError(schema=None, data=df)

    return df
