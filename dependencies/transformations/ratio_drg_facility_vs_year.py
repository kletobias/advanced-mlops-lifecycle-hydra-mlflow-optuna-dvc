# dependencies/transformations/ratio_drg_facility_vs_year.py
import logging
from dataclasses import dataclass
import pandas as pd
from dependencies.pandas_specific.df_merge import df_merge

logger = logging.getLogger(__name__)

@dataclass
class RatioDrgFacilityVsYearConfig:
    year_col_name: str
    facility_id_col_name: str
    apr_drg_code_col_name: str
    facility_drg_count_col_name: str
    year_drg_count_col_name: str
    ratio_drg_facility_vs_year_col_name: str
    year_merge_on: str
    year_merge_how: str
    final_merge_on: list[str]
    final_merge_how: str

def ratio_drg_facility_vs_year(
    df: pd.DataFrame,
    year_col_name: str,
    facility_id_col_name: str,
    apr_drg_code_col_name: str,
    facility_drg_count_col_name: str,
    year_drg_count_col_name: str,
    ratio_drg_facility_vs_year_col_name: str,
    year_merge_on: str,
    year_merge_how: str,
    final_merge_on: list[str],
    final_merge_how: str,
) -> pd.DataFrame:
    final_merge_on = list(final_merge_on)
    year_merge_on = str(year_merge_on)

    df_fac_yr = (
        df.groupby([year_col_name, facility_id_col_name])[apr_drg_code_col_name]
        .nunique()
        .reset_index(name=facility_drg_count_col_name)
    )

    df_yr = (
        df.groupby(year_col_name)[apr_drg_code_col_name]
        .nunique()
        .reset_index(name=year_drg_count_col_name)
    )

    df_fac_and_yr_merged = df_merge(
        df_fac_yr,
        df_yr,
        on=year_merge_on,
        how=year_merge_how,
    )

    df_fac_and_yr_merged[ratio_drg_facility_vs_year_col_name] = (
        df_fac_and_yr_merged[facility_drg_count_col_name] / df_fac_and_yr_merged[year_drg_count_col_name]
    )

    df_merged_back = df_merge(
        df,
        df_fac_and_yr_merged,
        on=final_merge_on,
        how=final_merge_how,
    )
    logger.info("Done with core transformation: ratio_drg_facility_vs_year")
    return df_merged_back
