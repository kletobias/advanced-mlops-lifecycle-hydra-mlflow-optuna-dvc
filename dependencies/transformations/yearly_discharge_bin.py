import logging
from dataclasses import dataclass

import pandas as pd
from dependencies.pandas_specific.df_merge import df_merge

logger = logging.getLogger(__name__)


@dataclass
class YearlyDischargeBinConfig:
    groupby_cols: str | list[str]
    as_index: bool
    sum_discharges_col_name: str
    rename_columns: dict[str, str]
    yearly_discharge_bin_col_name: str
    labels: bool
    duplicates: str
    num_bins: int
    year_col_name: str
    yearly_sum_discharges_col_name: str
    df_agg_columns: list[str]
    on_columns: list[str]
    how: str


def yearly_discharge_bin(
    df: pd.DataFrame,
    groupby_cols: str | list[str],
    as_index: bool,
    sum_discharges_col_name: str,
    rename_columns: dict[str, str],
    yearly_discharge_bin_col_name: str,
    labels: bool,
    duplicates: str,
    num_bins: int,
    year_col_name: str,
    yearly_sum_discharges_col_name: str,
    df_agg_columns: list[str],
    on_columns: list[str],
    how: str,
) -> pd.DataFrame:
    if isinstance(groupby_cols, str):
        groupby_cols = [groupby_cols]
    else:
        groupby_cols = list(groupby_cols)

    as_index = bool(as_index)
    on_columns = list(on_columns)

    def make_qbins(x, q):
        return pd.qcut(x, q=q, labels=labels, duplicates=duplicates)

    df_agg = (
        df.groupby(groupby_cols, as_index=as_index)[sum_discharges_col_name]
        .sum()
        .rename(columns=rename_columns)
    )

    df_agg[yearly_discharge_bin_col_name] = df_agg.groupby(year_col_name)[
        yearly_sum_discharges_col_name
    ].transform(lambda x: make_qbins(x, q=num_bins))

    logger.info("Done with core transformation: yearly_discharge_bin")
    return df_merge(
        df,
        df_agg[df_agg_columns],
        on=on_columns,
        how=how,
    )
