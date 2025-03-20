# dependencies/config_schemas/RootConfig.py
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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
    data_version: Optional[str] = None


@dataclass
class HydraConfig:
    job: Dict[str, str]
    run: Dict[str, str]
    sweep: Dict[str, str]


@dataclass
class LoggingUtilsConfig:
    log_directory_path: str
    log_file_path: str
    formatter: str
    level: int
    log_cfg_job: Dict[str, Any]


@dataclass
class MLExperimentsConfig:
    rng_seed: int
    n_jobs_study: int
    n_jobs_final_model: int
    target_col_modeling: str
    year_col: str
    train_range: List[int]
    val_range: List[int]
    test_range: List[int]
    experiment_prefix: str
    experiment_id: str
    artifact_directory_path: str
    permutation_importances_filename: str
    randomforest_importances_filename: str
    top_n_importances: int
    optuna_n_trials: int
    cv_splits: int
    direction: str
    scoring: Dict[str, str]


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
    drop_description_columns: Optional[DropDescriptionColumnsConfig] = None
    drop_non_lag_columns: Optional[DropNonLagColumnsConfig] = None
    drop_rare_drgs: Optional[DropRareDrgsConfig] = None
    ratio_drg_facility_vs_year: Optional[RatioDrgFacilityVsYearConfig] = None
    yearly_discharge_bin: Optional[YearlyDischargeBinConfig] = None
    agg_severities: Optional[AggSeveritiesConfig] = None
    mean_profit: Optional[MeanProfitConfig] = None
    median_profit: Optional[MedianProfitConfig] = None
    total_mean_cost: Optional[TotalMeanCostConfig] = None
    total_mean_profit: Optional[TotalMeanProfitConfig] = None
    total_median_cost: Optional[TotalMedianCostConfig] = None
    total_median_profit: Optional[TotalMedianProfitConfig] = None
    lag_columns: Optional[LagColumnsConfig] = None
    rolling_columns: Optional[RollingColumnsConfig] = None


@dataclass
class CsvToDataframeConfig:
    csv_file_path: str
    low_memory: bool


@dataclass
class DataframeToCsvConfig:
    output_file_path_csv: str
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
    input_file_path_csv: str
    input_file_path_json: str
    input_file_path_db: str
    input_metadata_file_path: str
    output_file_path_csv: str
    output_file_path_json: str
    output_file_path_db: str
    output_metadata_file_path: str

@dataclass
class StageConfig:
    name: str
    cmd_python: Optional[str] = None
    script: Optional[str] = None
    overrides: Optional[Dict[str, Any]] = field(default_factory=dict)
    deps: Optional[List[str]] = field(default_factory=list)
    outs: Optional[List[str]] = field(default_factory=list)

@dataclass
class Pipeline:
    stages: Optional[List[StageConfig]] = field(default_factory=list)
    stages_list: Optional[List[StageConfig]] = field(default_factory=list)
    stages_to_run: Optional[List[str]] = field(default_factory=list)
    force_run: Optional[bool] = None
    pipeline_run: Optional[bool] = None
    allow_dvc_changes: Optional[bool] = None
    skip_generation: Optional[bool] = None
    search_path: Optional[str] = None
    template_name: Optional[str] = None
    dvc_yaml_file_path: Optional[str] = None
    log_file_path: Optional[str] = None


@dataclass
class PipelineConfig:
    pipeline: Optional[Pipeline] = None

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
