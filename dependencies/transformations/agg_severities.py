# dependencies/transformations/agg_severities.py
import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class AggSeveritiesConfig:
    weighted_mean_weight_col_name: str
    weighted_median_weight_col_name: str
    discharges_col_name: str
    sum_discharges_key: str
    severity_levels: list[int]
    apr_severity_of_illness_code_col_name: str
    mean_cols: list[str]
    median_cols: list[str]
    groupby_cols: list[str]
    as_index: bool

def agg_severities(
    df: pd.DataFrame,
    weighted_mean_weight_col_name: str,
    weighted_median_weight_col_name: str,
    discharges_col_name: str,
    sum_discharges_key: str,
    severity_levels: list[int],
    apr_severity_of_illness_code_col_name: str,
    mean_cols: list[str],
    median_cols: list[str],
    groupby_cols: list[str],
    as_index: bool,
) -> pd.DataFrame:
    def weighted_mean(grp: pd.DataFrame, value_col: str, weight_col: str) -> float:
        total_wt = grp[weight_col].sum()
        return (
            np.nan
            if total_wt == 0
            else (grp[value_col] * grp[weight_col]).sum() / total_wt
        )

    def weighted_median(grp: pd.DataFrame, value_col: str, weight_col: str) -> float:
        df_sorted = grp[[value_col, weight_col]].sort_values(value_col)
        cumsum = df_sorted[weight_col].cumsum()
        half = df_sorted[weight_col].sum() / 2.0
        return df_sorted.loc[cumsum >= half, value_col].iloc[0]

    def aggregate_facility_rows(grp: pd.DataFrame) -> pd.Series:
        total_dis = grp[discharges_col_name].sum()
        results = {sum_discharges_key: total_dis}
        for severity_level in severity_levels:
            severity_level = int(severity_level)
            sub = grp[grp[apr_severity_of_illness_code_col_name] == severity_level]
            results[f"severity_{severity_level}_portion"] = (
                sub[discharges_col_name].sum() / total_dis if total_dis else 0
            )
        for col in mean_cols:
            if col in grp.columns:
                results[f"w_{col}"] = weighted_mean(grp, value_col=col, weight_col=weighted_mean_weight_col_name)

        for col in median_cols:
            if col in grp.columns:
                results[f"w_{col}"] = weighted_median(grp, value_col=col, weight_col=weighted_median_weight_col_name)
        return pd.Series(results)

    groupby_cols = list(groupby_cols)
    as_index = bool(as_index)
    aggregated = df.groupby(groupby_cols, as_index=as_index).apply(aggregate_facility_rows)
    aggregated = aggregated.reset_index(drop=False)
    logger.info("Done with core transformation: agg_severities")
    assert 'w_total_median_profit' in aggregated.columns.tolist(), "'w_total_median_profit' not in columns!"
    return aggregated
