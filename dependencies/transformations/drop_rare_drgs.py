import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DropRareDrgsConfig:
    apr_drg_code_col_name: str
    as_index: bool
    discharges_col_name: str
    threshold: int
    drop: bool
    inplace: bool = False


def drop_rare_drgs(
    df: pd.DataFrame,
    apr_drg_code_col_name: str,
    as_index: bool,
    discharges_col_name: str,
    threshold: int,
    drop: bool,
    inplace: bool,
) -> pd.DataFrame:
    as_index = bool(as_index)
    drop = bool(drop)
    inplace = bool(inplace)

    total_dis_by_code = df.groupby(apr_drg_code_col_name, as_index=as_index)[
        discharges_col_name
    ].sum()

    if as_index:
        valid_codes = total_dis_by_code.loc[total_dis_by_code > threshold].index
    else:
        valid_codes = total_dis_by_code.loc[
            total_dis_by_code[discharges_col_name] > threshold,
            apr_drg_code_col_name,
        ]

    df = df.loc[df[apr_drg_code_col_name].isin(valid_codes), :]
    df = pd.DataFrame(df.reset_index(drop=drop, inplace=inplace))
    logger.info("Done with core transformation: drop_rare_drgs")

    return df
