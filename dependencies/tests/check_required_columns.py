# dependencies/validations/check_required_columns.py
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pandera.errors as pe


@dataclass
class CheckRequiredColumnsConfig:
    required_columns: list[str] | None = None


def check_required_columns(
    df: pd.DataFrame, required_columns: list[str]
) -> pd.DataFrame:
    missing = [str(c) for c in required_columns if c not in df.columns]
    if missing:
        raise pe.SchemaError(
            schema=None,
            data=df,
            message=f"Missing columns: {missing}",
        )
    return df
