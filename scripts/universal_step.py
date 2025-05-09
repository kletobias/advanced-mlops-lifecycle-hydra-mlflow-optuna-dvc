# scripts/universal_step.py
"""Run one data-pipeline step chosen by Hydra config."""
import logging

import hydra
import pandas as pd

from dependencies.cleaning.sanitize_column_names import sanitize_column_names
from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.ingestion.ingest_data import (
    IngestDataConfig,
    ingest_data,
)
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_cfg_job import log_cfg_job
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.logging_utils.setup_logging import setup_logging
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.modeling.rf_optuna_trial import RfOptunaTrialConfig, rf_optuna_trial
from dependencies.modeling.ridge_optuna_trial import (
    RidgeOptunaTrialConfig,
    ridge_optuna_trial,
)
from dependencies.transformations.agg_severities import (
    AggSeveritiesConfig,
    agg_severities,
)
from dependencies.transformations.drop_description_columns import (
    DropDescriptionColumnsConfig,
    drop_description_columns,
)
from dependencies.transformations.drop_non_lag_columns import (
    DropNonLagColumnsConfig,
    drop_non_lag_columns,
)
from dependencies.transformations.drop_rare_drgs import (
    DropRareDrgsConfig,
    drop_rare_drgs,
)
from dependencies.transformations.lag_columns import LagColumnsConfig, lag_columns
from dependencies.transformations.mean_profit import MeanProfitConfig, mean_profit
from dependencies.transformations.median_profit import MedianProfitConfig, median_profit
from dependencies.transformations.ratio_drg_facility_vs_year import (
    RatioDrgFacilityVsYearConfig,
    ratio_drg_facility_vs_year,
)
from dependencies.transformations.rolling_columns import (
    RollingColumnsConfig,
    rolling_columns,
)
from dependencies.transformations.total_mean_cost import (
    TotalMeanCostConfig,
    total_mean_cost,
)
from dependencies.transformations.total_mean_profit import (
    TotalMeanProfitConfig,
    total_mean_profit,
)
from dependencies.transformations.total_median_cost import (
    TotalMedianCostConfig,
    total_median_cost,
)
from dependencies.transformations.total_median_profit import (
    TotalMedianProfitConfig,
    total_median_profit,
)
from dependencies.transformations.yearly_discharge_bin import (
    YearlyDischargeBinConfig,
    yearly_discharge_bin,
)

TRANSFORMATIONS = {
    "ingest_data": {
        "transform": log_function_call(ingest_data),
        "Config": IngestDataConfig,
    },
    "sanitize_column_names": {
        "transform": log_function_call(sanitize_column_names),
        "Config": None,
    },
    "agg_severities": {
        "transform": log_function_call(agg_severities),
        "Config": AggSeveritiesConfig,
    },
    "drop_description_columns": {
        "transform": log_function_call(drop_description_columns),
        "Config": DropDescriptionColumnsConfig,
    },
    "drop_non_lag_columns": {
        "transform": log_function_call(drop_non_lag_columns),
        "Config": DropNonLagColumnsConfig,
    },
    "drop_rare_drgs": {
        "transform": log_function_call(drop_rare_drgs),
        "Config": DropRareDrgsConfig,
    },
    "lag_columns": {
        "transform": log_function_call(lag_columns),
        "Config": LagColumnsConfig,
    },
    "mean_profit": {
        "transform": log_function_call(mean_profit),
        "Config": MeanProfitConfig,
    },
    "median_profit": {
        "transform": log_function_call(median_profit),
        "Config": MedianProfitConfig,
    },
    "ratio_drg_facility_vs_year": {
        "transform": log_function_call(ratio_drg_facility_vs_year),
        "Config": RatioDrgFacilityVsYearConfig,
    },
    "rolling_columns": {
        "transform": log_function_call(rolling_columns),
        "Config": RollingColumnsConfig,
    },
    "total_mean_cost": {
        "transform": log_function_call(total_mean_cost),
        "Config": TotalMeanCostConfig,
    },
    "total_mean_profit": {
        "transform": log_function_call(total_mean_profit),
        "Config": TotalMeanProfitConfig,
    },
    "total_median_cost": {
        "transform": log_function_call(total_median_cost),
        "Config": TotalMedianCostConfig,
    },
    "total_median_profit": {
        "transform": log_function_call(total_median_profit),
        "Config": TotalMedianProfitConfig,
    },
    "yearly_discharge_bin": {
        "transform": log_function_call(yearly_discharge_bin),
        "Config": YearlyDischargeBinConfig,
    },
    "rf_optuna_trial": {
        "transform": log_function_call(rf_optuna_trial),
        "Config": RfOptunaTrialConfig,
    },
    "ridge_optuna_trial": {
        "transform": log_function_call(ridge_optuna_trial),
        "Config": RidgeOptunaTrialConfig,
    },
}


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def universal_step(cfg: RootConfig) -> None:
    """Dispatch to the step in `TRANSFORMATIONS`, handle I/O, log, exit."""
    setup_logging(cfg)
    logger = logging.getLogger(__name__)

    log_cfg_job_flag = cfg.logging_utils.log_cfg_job.log_for_each_step
    if log_cfg_job_flag:
        logger.info("Override: 'log_cfg_job_flag' set to %s", bool(log_cfg_job_flag))
        log_cfg_job(cfg)
    else:
        logger.debug(
            "Not logging cfg job: 'log_cfg_job_flag' == %s",
            bool(log_cfg_job_flag),
        )

    transform_name = cfg.setup.script_base_name
    if transform_name not in TRANSFORMATIONS:
        logger.error("'%s' is not recognized in TRANSFORMATIONS.", transform_name)
        return

    step_info = TRANSFORMATIONS[transform_name]
    step_fn = step_info["transform"]
    step_cls = step_info["Config"]

    step_params = cfg.transformations[transform_name]

    read_input = cfg.io_policy.READ_INPUT
    write_output = cfg.io_policy.WRITE_OUTPUT

    if transform_name == "ingest_data":
        if step_cls:
            cfg_obj = step_cls(**step_params)
            step_fn(**cfg_obj.__dict__)
        else:
            step_fn()
    else:
        if read_input:
            df = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
        else:
            df = pd.DataFrame()

        cfg_obj = step_cls(**step_params) if step_cls else None
        returned_value = step_fn(df, **(cfg_obj.__dict__ if cfg_obj else {}))

        if cfg.transformations.RETURNS == "df" and returned_value is not None:
            if not isinstance(returned_value, pd.DataFrame):
                msg = f"{transform_name} did not return a DataFrame."
                raise TypeError(msg)
            df = returned_value

        if write_output:
            dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
            calculate_and_save_metadata(
                df,
                **cfg.utility_functions.calculate_and_save_metadata,
            )

    logger.info("Sucessfully executed step: %s", transform_name)


if __name__ == "__main__":
    universal_step()
