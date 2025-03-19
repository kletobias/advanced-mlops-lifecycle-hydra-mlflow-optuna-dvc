# === config_schemas/RootConfig.py ===
# UPDATED to align with the universal-step approach and typed transformation configs

from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict

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
class DownloadConfig:
    dataset: str
    target_dir: str
    zip_filename: str
    csv_filename: str


@dataclass
class DefaultDatabaseTableNamesConfig:
    input_data: str
    output_data: str


@dataclass
class DataVersionsConfig:
    name: str
    data_version_input: str
    data_version_output: str
    description: str
    default_database_table_names: DefaultDatabaseTableNamesConfig
    download: DownloadConfig


@dataclass
class HydraJobLoggingConfig:
    handlers: Dict[str, Dict[str, str]]


@dataclass
class HydraConfig:
    job: Dict[str, str]
    run: Dict[str, str]
    sweep: Dict[str, str]
    job_logging: HydraJobLoggingConfig


@dataclass
class LoggingUtilsConfig:
    log_directory_path: str
    log_file_path: str
    formatter: str
    level: str


@dataclass
class CVConfig:
    type: str
    n_splits: int
    shuffle: bool
    random_state: int


@dataclass
class MLFlowConfig:
    output_directory_path: str
    experiment_id: str
    experiment_directory_path: str
    artifact_directory_path: str
    permutation_importances_filename: str
    tracking_uri: Optional[str]
    feature_importances_artifact_sub_dir: str
    final_model_artifact_sub_dir: str


@dataclass
class MLExperimentsConfig:
    cv: CVConfig
    mlflow: MLFlowConfig
    top_n_importances: int


@dataclass
class ModelsConfig:
    models_in_project: List[str]


@dataclass
class OutputsConfig:
    script_outputs_directory: str
    timestamp: str
    script_cfg_job_file_path: str


@dataclass
class PathsDirectoriesConfig:
    project_root: str
    dependencies: str
    configs: str
    bin: str
    data: str
    outputs: str
    src: str
    templates: str
    logs: str
    models: str
    docs: str


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
    script_template_directory_path: str
    script_template_filename: str
    script_template_file_path: str
    script_base_name: str
    script_filename: str
    script_directory_path: str
    script_file_path: str


@dataclass
class DataStorageReadcsvoptionsConfig:
    low_memory: bool


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
    read_csv_options: DataStorageReadcsvoptionsConfig


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
class UtilityFunctionsConfig:
    pass


@dataclass
class RootConfig:
    data_storage: DataStorageConfig
    data_versions: DataVersionsConfig
    hydra: HydraConfig
    logging_utils: LoggingUtilsConfig
    ml_experiments: MLExperimentsConfig
    models: ModelsConfig
    outputs: OutputsConfig
    paths: PathsConfig
    setup: SetupConfig
    project_sections: ProjectSectionConfig
    transformations: TransformationsConfig
    utility_functions: UtilityFunctionsConfig


cs = ConfigStore.instance()

cs.store(group="utility_functions", name="base_schema", node=UtilityFunctionsConfig)
cs.store(group="transformations", name="base_schema", node=TransformationsConfig)
cs.store(group="data_storage", name="base_schema", node=DataStorageConfig)
cs.store(group="data_versions", name="base_schema", node=DataVersionsConfig)
cs.store(group="hydra", name="default_schema", node=HydraConfig)
cs.store(group="logging_utils", name="default_schema", node=LoggingUtilsConfig)
cs.store(group="ml_experiments", name="base_schema", node=MLExperimentsConfig)
cs.store(group="models", name="base_schema", node=ModelsConfig)
cs.store(group="outputs", name="default_schema", node=OutputsConfig)
cs.store(group="paths", name="default_schema", node=PathsConfig)
cs.store(group="project_sections", name="example", node=ProjectSectionConfig)
cs.store(group="setup", name="base_schema", node=SetupConfig)

# Register the final RootConfig so Hydra knows how to instantiate it
cs.store(name="root_config", node=RootConfig)
