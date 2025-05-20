# dependencies/config_schemas/RootConfig.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

from dependencies.ingestion.ingest_data import IngestDataConfig
from dependencies.tests.check_required_columns import CheckRequiredColumnsConfig
from dependencies.tests.check_row_count import CheckRowCountConfig
from dependencies.transformations.agg_severities import AggSeveritiesConfig
from dependencies.transformations.drop_description_columns import (
    DropDescriptionColumnsConfig,
)
from dependencies.transformations.drop_non_lag_columns import DropNonLagColumnsConfig
from dependencies.transformations.drop_rare_drgs import DropRareDrgsConfig
from dependencies.transformations.lag_columns import LagColumnsConfig
from dependencies.transformations.mean_profit import MeanProfitConfig
from dependencies.transformations.median_profit import MedianProfitConfig
from dependencies.transformations.ratio_drg_facility_vs_year import (
    RatioDrgFacilityVsYearConfig,
)
from dependencies.transformations.rolling_columns import RollingColumnsConfig
from dependencies.transformations.total_mean_cost import TotalMeanCostConfig
from dependencies.transformations.total_mean_profit import TotalMeanProfitConfig
from dependencies.transformations.total_median_cost import TotalMedianCostConfig
from dependencies.transformations.total_median_profit import TotalMedianProfitConfig
from dependencies.transformations.yearly_discharge_bin import YearlyDischargeBinConfig


@dataclass
class IOPolicyConfig:
    READ_INPUT: bool = True
    WRITE_OUTPUT: bool = True


@dataclass
class DataVersionsConfig:
    name: str = MISSING
    data_version_input: str = MISSING
    data_version_output: str = MISSING
    description: str = MISSING
    dataset_url: str = MISSING
    data_version: str | None = None


@dataclass
class HydraConfig:
    job: dict[str, str] | None = field(default_factory=dict)
    run: dict[str, str] | None = field(default_factory=dict)
    sweep: dict[str, str] | None = field(default_factory=dict)


@dataclass
class LogCfgJobConfig:
    log_for_each_step: bool = False
    output_cfg_job_directory_path: str = MISSING
    output_cfg_job_file_path: str = MISSING
    resolve: bool = True


@dataclass
class LoggingUtilsConfig:
    log_directory_path: str = MISSING
    log_file_path: str = MISSING
    formatter: str = "%(asctime)s %(levelname)s:%(message)s"
    level: int = 20
    log_cfg_job: LogCfgJobConfig = field(default_factory=LogCfgJobConfig)


@dataclass
class MLExperimentsConfig:
    rng_seed: int = MISSING
    n_jobs_study: int = MISSING
    n_jobs_final_model: int = MISSING
    target_col_modeling: str = MISSING
    year_col: str = MISSING
    train_range: list[int] | None = field(default_factory=list)
    val_range: list[int] | None = field(default_factory=list)
    test_range: list[int] | None = field(default_factory=list)
    experiment_prefix: str = MISSING
    experiment_id: str = MISSING
    artifact_directory_path: str = MISSING
    permutation_importances_filename: str = MISSING
    randomforest_importances_filename: str = MISSING
    top_n_importances: int = MISSING
    optuna_n_trials: int = MISSING
    cv_splits: int = MISSING
    direction: str = MISSING
    scoring: dict[str, str] | None = field(default_factory=dict)


@dataclass
class PathsDirectoriesConfig:
    project_root: str = MISSING
    bin: str = MISSING
    configs: str = MISSING
    data: str = MISSING
    dependencies: str = MISSING
    documentation: str = MISSING
    logs: str = MISSING
    outputs: str = MISSING
    scripts: str = MISSING
    templates: str = MISSING


@dataclass
class PathsConfig:
    directories: PathsDirectoriesConfig | None = field(
        default_factory=PathsDirectoriesConfig
    )


@dataclass
class ProjectSectionConfig:
    id: int = MISSING
    name: str = MISSING
    alias: str = MISSING


@dataclass
class SetupConfig:
    script_base_name: str = MISSING


@dataclass
class ColumnNamesConfig:
    unit_col_name: str = "unit"


# Each field is an optional typed config for that transformation,
# plus "name" to specify which transform to run in universal_step.
@dataclass
class TransformationsConfig:
    check_required_columns: bool
    check_row_count: bool
    return_type: str
    name: str
    ingest_data: IngestDataConfig | None
    drop_description_columns: DropDescriptionColumnsConfig | None
    drop_non_lag_columns: DropNonLagColumnsConfig | None
    drop_rare_drgs: DropRareDrgsConfig | None
    ratio_drg_facility_vs_year: RatioDrgFacilityVsYearConfig | None
    yearly_discharge_bin: YearlyDischargeBinConfig | None
    agg_severities: AggSeveritiesConfig | None
    mean_profit: MeanProfitConfig | None
    median_profit: MedianProfitConfig | None
    total_mean_cost: TotalMeanCostConfig | None
    total_mean_profit: TotalMeanProfitConfig | None
    total_median_cost: TotalMedianCostConfig | None
    total_median_profit: TotalMedianProfitConfig | None
    lag_columns: LagColumnsConfig | None
    rolling_columns: RollingColumnsConfig | None


@dataclass
class UtilityFunctionReadConfig:
    """Parameters for reading CSV."""

    input_file_path: str = MISSING
    low_memory: bool = False


@dataclass
class UtilityFunctionWriteConfig:
    """Parameters for writing to CSV."""

    output_file_path: str = MISSING
    include_index: bool = False


@dataclass
class UtilityFunctionMetadataConfig:
    """Parameters for generating and saving metadata."""

    data_file_path: str = MISSING
    output_metadata_file_path: str = MISSING


@dataclass
class UtilityFunctionsConfig:
    """
    Combines read, write, and metadata config under a single Hydra group,
    to keep them together but still allow dictionary unpacking in universal_step.
    """

    utility_function_read: UtilityFunctionReadConfig = field(
        default_factory=UtilityFunctionReadConfig
    )
    utility_function_write: UtilityFunctionWriteConfig = field(
        default_factory=UtilityFunctionWriteConfig
    )
    utility_function_metadata: UtilityFunctionMetadataConfig = field(
        default_factory=UtilityFunctionMetadataConfig
    )


@dataclass
class DataStorageConfig:
    # Number of fields: 10
    split: str = MISSING
    suffix: str = MISSING
    input_file_extension: str = MISSING
    output_file_extension: str = MISSING
    input_metadata_file_extension: str = MISSING
    output_metadata_file_extension: str = MISSING
    input_params_file_extension: str = "yaml"
    output_params_file_extension: str = "yaml"
    input_params_file_path: str = MISSING
    output_params_file_path: str = MISSING
    input_file_path: str = MISSING
    input_metadata_file_path: str = MISSING
    output_file_path: str = MISSING
    output_metadata_file_path: str = MISSING
    run_id_outputs_directory_path: str = MISSING


@dataclass
class StageConfig:
    name: str = MISSING
    cmd_python: str | None = None
    script: str | None = None
    overrides: dict[str, Any] | None = field(default_factory=dict)
    desc: str | None = None
    frozen: bool | None = None
    deps: list[str] | None = field(default_factory=list)
    outs: list[str] | None = field(default_factory=list)


@dataclass
class PlotConfig:
    template: str | None = None
    x: str | None = None
    y: str | None = None


@dataclass
class Pipeline:
    stages: list[StageConfig] | None = field(default_factory=list)
    plots: list[PlotConfig] | None = field(default_factory=list)
    stages_to_run: list[str] | None = field(default_factory=list)
    force_run: bool | None = None
    pipeline_run: bool | None = None
    allow_dvc_changes: bool | None = None
    skip_generation: bool | None = None
    search_path: str | None = None
    template_name: str | None = None
    dvc_yaml_file_path: str | None = None
    log_file_path: str | None = None


@dataclass
class TestsConfig:
    check_required_columns: CheckRequiredColumnsConfig | None
    check_row_count: CheckRowCountConfig | None


@dataclass
class TestParamsConfig:
    required_columns: list[str] | None = field(default_factory=list)
    row_count_original: int | None = None
    row_count_aggregated: int | None = None


@dataclass
class RootConfig:
    transformations: TransformationsConfig | None
    tests: TestsConfig | None
    cmd_python: str = "$CMD_PYTHON"
    universal_step_script: str = "scripts/universal_step.py"
    dvc_default_desc: str = "Refer to deps/outs for details."
    rng_seed: int = 42
    data_versions: DataVersionsConfig = field(default_factory=DataVersionsConfig)
    hydra: HydraConfig = field(default_factory=HydraConfig)
    logging_utils: LoggingUtilsConfig = field(default_factory=LoggingUtilsConfig)
    ml_experiments: MLExperimentsConfig = field(default_factory=MLExperimentsConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    setup: SetupConfig = field(default_factory=SetupConfig)
    project_sections: ProjectSectionConfig = field(default_factory=ProjectSectionConfig)
    pipeline: Pipeline = field(default_factory=Pipeline)
    io_policy: IOPolicyConfig = field(default_factory=IOPolicyConfig)
    utility_functions: UtilityFunctionsConfig = field(
        default_factory=UtilityFunctionsConfig
    )
    data_storage: DataStorageConfig = field(default_factory=DataStorageConfig)
    test_params: TestParamsConfig = field(default_factory=TestParamsConfig)


cs = ConfigStore.instance()

cs.store(group="io_policy", name="base_schema", node=IOPolicyConfig)
cs.store(group="utility_functions", name="base_schema", node=UtilityFunctionsConfig)
cs.store(group="transformations", name="base_schema", node=TransformationsConfig)
cs.store(group="data_storage", name="base_schema", node=DataStorageConfig)
cs.store(group="tests", name="base_schema", node=TestsConfig)
cs.store(group="test_params", name="base_schema", node=TestParamsConfig)
cs.store(group="data_versions", name="base_schema", node=DataVersionsConfig)
cs.store(group="hydra", name="default_schema", node=HydraConfig)
cs.store(group="logging_utils", name="default_schema", node=LoggingUtilsConfig)
cs.store(group="ml_experiments", name="base_schema", node=MLExperimentsConfig)
cs.store(group="paths", name="default_schema", node=PathsConfig)
cs.store(group="project_sections", name="example", node=ProjectSectionConfig)
cs.store(group="setup", name="base_schema", node=SetupConfig)
cs.store(group="pipeline", name="base_schema", node=Pipeline)

# Register the final RootConfig so Hydra knows how to instantiate it
cs.store(name="root_config", node=RootConfig)
