# dependencies/config_schemas/RootConfig.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hydra.core.config_store import ConfigStore

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
class DataVersionsConfig:
    name: str
    data_version_input: str
    data_version_output: str
    description: str
    dataset_url: str
    data_version: str | None = None


@dataclass
class HydraConfig:
    job: dict[str, str]
    run: dict[str, str]
    sweep: dict[str, str]


@dataclass
class LoggingUtilsConfig:
    log_directory_path: str
    log_file_path: str
    formatter: str
    level: int
    log_cfg_job: dict[str, Any]


@dataclass
class MLExperimentsConfig:
    rng_seed: int
    n_jobs_study: int
    n_jobs_final_model: int
    target_col_modeling: str
    year_col: str
    train_range: list[int]
    val_range: list[int]
    test_range: list[int]
    experiment_prefix: str
    experiment_id: str
    artifact_directory_path: str
    permutation_importances_filename: str
    randomforest_importances_filename: str
    top_n_importances: int
    optuna_n_trials: int
    cv_splits: int
    direction: str
    scoring: dict[str, str]


@dataclass
class PathsDirectoriesConfig:
    project_root: str
    bin: str
    configs: str
    data: str
    dependencies: str
    documentation: str
    logs: str
    outputs: str
    scripts: str
    templates: str


@dataclass
class PathsConfig:
    directories: PathsDirectoriesConfig


@dataclass
class ProjectSectionConfig:
    id: int
    name: str
    alias: str


@dataclass
class SetupConfig:
    script_base_name: str


# Each field is an optional typed config for that transformation,
# plus "name" to specify which transform to run in universal_step.
@dataclass
class TransformationsConfig:
    name: str = "none"  # which transform is active (e.g. 'mean_profit')
    drop_description_columns: DropDescriptionColumnsConfig | None = None
    drop_non_lag_columns: DropNonLagColumnsConfig | None = None
    drop_rare_drgs: DropRareDrgsConfig | None = None
    ratio_drg_facility_vs_year: RatioDrgFacilityVsYearConfig | None = None
    yearly_discharge_bin: YearlyDischargeBinConfig | None = None
    agg_severities: AggSeveritiesConfig | None = None
    mean_profit: MeanProfitConfig | None = None
    median_profit: MedianProfitConfig | None = None
    total_mean_cost: TotalMeanCostConfig | None = None
    total_mean_profit: TotalMeanProfitConfig | None = None
    total_median_cost: TotalMedianCostConfig | None = None
    total_median_profit: TotalMedianProfitConfig | None = None
    lag_columns: LagColumnsConfig | None = None
    rolling_columns: RollingColumnsConfig | None = None


@dataclass
class CsvToDataframeConfig:
    file_path: str
    low_memory: bool


@dataclass
class DataframeToCsvConfig:
    output_file_path: str
    include_index: bool


@dataclass
class CalculateAndSaveMetadataConfig:
    data_file_path: str
    output_metadata_file_path: str


@dataclass
class UtilityFunctionsConfig:
    csv_to_dataframe: CsvToDataframeConfig
    dataframe_to_csv: DataframeToCsvConfig
    calculate_and_save_metadata: CalculateAndSaveMetadataConfig


@dataclass
class DataStorageConfig:
    input_file_path: str
    input_metadata_file_path: str
    output_file_path: str
    output_metadata_file_path: str


@dataclass
class StageConfig:
    name: str
    cmd_python: str | None = None
    script: str | None = None
    overrides: dict[str, Any] | None = field(default_factory=dict)
    desc: str | None = None
    frozen: bool | None = None
    deps: list[str] | None = field(default_factory=list)
    outs: list[str] | None = field(default_factory=list)


@dataclass
class PlotConfig:
    # Number of fields: 3
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
class PipelineConfig:
    pipeline: Pipeline | None = None


@dataclass
class RootConfig:
    data_storage: DataStorageConfig
    data_versions: DataVersionsConfig
    hydra: HydraConfig
    logging_utils: LoggingUtilsConfig
    ml_experiments: MLExperimentsConfig
    paths: PathsConfig
    setup: SetupConfig
    project_sections: ProjectSectionConfig
    transformations: TransformationsConfig
    utility_functions: UtilityFunctionsConfig
    pipeline: PipelineConfig


cs = ConfigStore.instance()

cs.store(group="utility_functions", name="base_schema", node=UtilityFunctionsConfig)
cs.store(group="transformations", name="base_schema", node=TransformationsConfig)
cs.store(group="data_storage", name="base_schema", node=DataStorageConfig)
cs.store(group="data_versions", name="base_schema", node=DataVersionsConfig)
cs.store(group="hydra", name="default_schema", node=HydraConfig)
cs.store(group="logging_utils", name="default_schema", node=LoggingUtilsConfig)
cs.store(group="ml_experiments", name="base_schema", node=MLExperimentsConfig)
cs.store(group="paths", name="default_schema", node=PathsConfig)
cs.store(group="project_sections", name="example", node=ProjectSectionConfig)
cs.store(group="setup", name="base_schema", node=SetupConfig)
cs.store(group="pipeline", name="base_schema", node=PipelineConfig)

# Register the final RootConfig so Hydra knows how to instantiate it
cs.store(name="root_config", node=RootConfig)
