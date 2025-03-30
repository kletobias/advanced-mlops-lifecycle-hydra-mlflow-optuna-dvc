<!--documentation/detailed_documentation.md-->

# Comprehensive Documentation

## README.md

### Key Features

#### Key Features - Quick Overview

- **Hydra Configuration**  
  All parameters (data paths, transformations, hyperparameters) are separated from the code in a single source of truth. With Hydra’s override syntax, you can quickly switch between data versions (e.g., v0, v1, …) or transformations (lag_columns, drop_rare_drgs, etc.) at runtime, without modifying your core Python scripts.

- **Smart use of defaults lists within config groups**
  We define the defaults for each config group within `base.yaml` files. These 'base' configs are added to the defaults list of more specific configs and overwritten only where needed. No duplication.

- **Data Versioning with DVC**  
  Each pipeline stage (e.g., ingestion, transformation, modeling) is only declared in `configs/pipeline/base.yaml` and written to `dvc.yaml`. DVC then tracks every data transformation, ensuring that any version of the dataset or code can be reproduced exactly. This eliminates confusion around which data was used for which experiment.

- **We added support for `plots` in pipeline/base.yaml**
  `dependencies/template/generate_dvc_yaml_core.py` now checks for plots in `configs/pipeline/base.yaml`. It generates the plots section in `dvc.yaml`, if present.

- **Experiment Tracking with MLflow**  
  Scripts like `rf_optuna_trial.py` or `ridge_optuna_trial.py` automatically log metrics and artifacts (model pickles, permutation importances, etc.) to MLflow (under MLflow's default folder `mlruns`). This makes it easy to compare multiple runs side by side, roll back to past models, or share results with your team.

- **Modular Transformations**  
  Each transformation is a small, testable function in `dependencies/transformations/`. The configuration for which columns to shift, which DRGs to drop, and other parameters lives in matching YAML files under `configs/transformations/`. This approach keeps transformations atomic and easy to swap in and out.

- **All Transformations share the same structure**
  Each includes one dataclass and one transformation function. We use a single-function-per-transformation approach to keep transformations concise and clear. Universal tasks—such as reading/writing data, metadata processing, or merging—are handled in a dedicated dependencies module. Any repeated logic across transformations is refactored into shared code, ensuring maintainability, clarity, and minimal duplication.

- **Metadata Logging**  
  Every time you generate a new CSV, the pipeline creates a JSON metadata file (including row count, column types, file hash, etc.). This extra layer of traceability helps ensure that any data artifacts you produce can be audited or reproduced later on.

#### Why Aim for this "Trifecta"?

Hydra, Optuna, and MLflow each solve critical but distinct challenges in a modern MLOps pipeline. Hydra provides flexible, hierarchical configuration management that ensures a single source of truth and reduces repetitive boilerplate. Optuna streamlines hyperparameter tuning through efficient search algorithms and automatic trial management. MLflow takes care of experiment tracking, artifact logging, and model versioning, making it simple to compare runs or roll back to a previous state. By weaving these tools into a unified workflow, you reap the benefits of advanced experimentation, reproducibility, and clean code organization—all while scaling to more complex data engineering and modeling tasks.

In short, this “trifecta” setup saves you time, reduces errors, and achieves scalable MLOps practices at both small and large organizations.

##### End-to-End Pipeline Management

**Single Source of Truth With Hydra**

One of the biggest pitfalls in MLOps is duplicating configuration values or scattering them across various scripts. Here, we use structured configs (with Python dataclasses) and Hydra’s override syntax to maintain one definition for each variable. When you need to change a path or hyperparameter, you do it once, and it propagates everywhere else automatically.

**Clean Separation of Concerns**

Our Python code is universal rather than specific to any single pipeline stage. We centralize logic in flexible, modular functions (e.g., transformations, model trainers, data ingestion routines) and tie them together with Hydra configs. This makes it trivial to add new functionality—like a novel data transformation or an entirely different model architecture—without duplicating scripts for each experiment.

**Override Syntax for Rapid Experimentation**

Switching data versions or transformations can be done with a few flags at runtime, rather than rewriting script after script. For example:

This runs the `RandomForestRegressor` optuna trial on the complete dataset.

```
python universal_step.py \
  setup.script_base_name=rf_optuna_trial \
  transformations=rf_optuna_trial \
  data_versions.data_version_input=v13 \
  io_policy.WRITE_OUTPUT=false \
  model_params=rf_optuna_trial_params
```

For debugging this optuna trial we used a smaller dataset, which is saved as data version `v13t`. We can run the trial using this version by simply changing`data_versions.data_version_input=v13` -> `data_versions.data_version_input=v13t`.

```
python universal_step.py \
  setup.script_base_name=rf_optuna_trial \
  transformations=rf_optuna_trial \
  data_versions.data_version_input=v13t \
  io_policy.WRITE_OUTPUT=false \
  model_params=rf_optuna_trial_params
```

You might wonder why we don't specify `data_versions.data_version_output`. The reason lies in how we defined `data_version_input`, and `data_version_output` in configs/data_versions/base.yaml:

```yaml
name: hospital_inpatient_cost_data_by_new_york_state
data_version_input: v0
data_version_output: ${.data_version_input}
description: |
  dataset name: `hospital_inpatient_cost_data_by_new_york_state`
  Original, unmodified data, as downloaded from kaggle.
  See 'dataset_url' for further information.

dataset_url: "https://www.kaggle.com/datasets/thedevastator/2010-new-york-state-hospital-inpatient-discharge"
```

The default for `data_version_output` is `data_version_output == data_version_input`.

This flexibility empowers you to iterate quickly without diving into complex code changes.

##### Why Companies Struggle

Organizations often fail at building a cohesive MLOps practice because they adopt these tools in isolation or rely on ad hoc scripts. Configuration drift and inconsistent versioning are common outcomes, making reproducing experiments or sharing code with new team members an uphill battle. This project addresses these pitfalls by maintaining a strict single source of truth, unifying the entire pipeline, and ensuring every stage is both reproducible and extensible.

By following these principles and leveraging the synergy of Hydra, Optuna, and MLflow, you build a solid foundation for any enterprise-scale MLOps workflow—one that’s modular, reproducible, and effortless to extend as your data and modeling needs evolve.

## Chapter 1 - High-Level Overview

### Objectives and Motivations

- **Robust Reproducibility**  
  The pipeline uses DVC to track all data transformations, ensuring every version of the dataset and code is fully reproducible. This guarantees stability and verifiability for ML pipelines in production. Stages `v5_1_total_median_cost` and `v5_2_total_mean_cost` demonstrate how new transformations can be seamlessly inserted at any point in the pipeline.

- **Flexibility and Maintainability**  
  Hydra and Omegaconf power hierarchical configurations: you can shift between data versions (`v0`, `v1`...) or transformations (`drop_rare_drgs`, `lag_columns`, `rolling_columns`) just by changing a single line in a YAML config instead of rewriting scripts.

- **Single Source of Truth**  
  Paths, hyperparameters, and experiment details live in config groups rather than scattered across code. This keeps the pipeline maintainable—no duplication of parameters.

- **End-to-End Logging and Experiment Tracking**  
  MLflow hooks into each experiment to log artifacts (pickle models, permutation importances) and metrics (RMSE, R2), making it straightforward to roll back or compare runs.

### Architecture Highlights

- **Modular Transformations**  
  Every data-manipulation step is a dedicated Python module under `dependencies/transformations/`. The pipeline calls them with Hydra overrides, so it’s easy to add or remove transformations without altering the central code.

- **Universal Execution Script**  
  A single `universal_step.py` file processes all transformations. It reads instructions from Hydra configs, encapsulates them in the correct dataclass, loads input data, runs the specified transformation function, and writes the output plus metadata. This approach unifies ingestion, cleaning, feature engineering, and modeling steps under one script.

- **DVC Data Lineage**  
  Each transformation stage is also declared in the pipeline (`configs/pipeline/base.yaml`). DVC ensures a reproducible sequence of transformations. A new data version always references exactly which code and hyperparameters created it.

- **Optuna Hyperparameter Optimization**  
  Two lines of config can switch from “random search” to a more advanced approach. The pipeline orchestrates parallel trials for model tuning while respecting available CPU cores (validated via custom concurrency checks).

- **Metadata-Driven**  
  Every output CSV is accompanied by a JSON file capturing row counts, column data types, hashing for integrity checks, etc. This supports audits or debugging if the data is later found to be inconsistent.

- **Seamless MLflow Integration**  
  Each ML training run logs to the same MLflow folder. The best model is automatically saved as a .pkl artifact, with optional random forest or permutation-based feature importances logged to CSV. Simple queries in MLflow show how hyperparameters affected performance historically.

- **Config Grouping and Overrides**  
  The code is decoupled from environment specifics: data version, hyperparameters, logging levels, etc. By altering Hydra overrides, you can run the same pipeline with different storage backends or hyperparameter sets without rewriting any logic.

- **Scalable for Large Teams**  
  Clear separation of concerns (data transformation, logging, model training) and advanced version control (DVC + Git) means multiple developers can iterate on different transformations or models concurrently, each pinned to a distinct data version.

These design choices demonstrate a thorough MLOps-oriented approach—one that ensures both reproducibility and agility for rapid experimentation in a real-world setting.

## Chapter 2 - Config Groups and Rationale

### Overall Structure

- **Separation of Concerns**  
  Config files are split into logical groups: `data_versions/`, `models/`, `ml_experiments/`, `transformations/`, etc. Each group handles a well-defined aspect of the pipeline (e.g., which dataset version to read, how hyperparameters are set for RandomForest vs. Ridge, how transformations are chained).

- **Override-Driven**  
  By default, `config.yaml` references `defaults: [...]`. But at runtime, you can override any part of these defaults (for example, switching from `v7` to `v10` data) without editing code. This makes the pipeline highly flexible for new data or new model types.

- **Reduced Duplication**  
  Each configuration property lives in exactly one file—no repeated paths or hyperparameters in multiple scripts. Hydra merges them at runtime into a single “global” config. When you want a new data version, you simply add a `v11.yaml` file describing how it differs from the previous version.

- **Future-Proof**  
  This modular approach scales as you add more transformations, new data splits, or additional advanced hyperparameter search spaces. You won’t have to refactor your entire codebase—just extend or create new config files.

### Notable Folders

- **`configs/data_versions/`**  
  All shared logic is located in `base.yaml`. You only need to define the input and output data versions as overrides. All other `.yaml` files document the dataset’s evolution, detailing any new transformations or features at each step. DVC references these versions, allowing you to reproduce any specific data state.

- **`configs/transformations/`**  
  Mappings for each Python transformation function. For example, `lag_columns.yaml` defines which columns to shift, while `rolling_columns.yaml` sets rolling windows. The main pipeline references these transformations in a stage-wise manner.

- **`configs/model_params/`**  
  This approach uses Hydra’s advanced defaults list to reference a separate config group for model parameters. By employing slash notation (for example, /model_params: rf_optuna_trial_params) in a machine learning hyperparameter optimization transformation’s defaults list, each stage seamlessly merges in the base hyperparameter definitions without overwriting fields. The rf_optuna_trial_params config itself points to a shared random forest parameter file, so you always inherit the complete hyperparameter dictionary. You can override only the parts you want to change for that transformation, and you can also add new hyperparameters specific to your current experiment. These overrides are non-destructive, meaning they leave all other definitions intact. This design keeps all model parameters in a single place while letting each step pull exactly what it needs.

- **`configs/pipeline/`**  
  Ties everything together. `base.yaml` enumerates each stage in the data transformation sequence, while specialized YAMLs (like `orchestrate_dvc_flow.yaml`) define how DVC is orchestrated. Each stage points to a script plus overrides for `setup.script_base_name`. If plots are found, the resulting `dvc.yaml` will include them as well.

- **`configs/ml_experiments/`**  
  Centralizes experiment-level settings: random seeds, train/val/test ranges, or the name of the MLflow experiment folder. Makes it easy to manage or switch between multiple experiment setups. `base.yaml` defines what is shared, with `rf_optuna_trial.yaml`, and `ridge_optuna_trial.yaml` only overriding what changes.

- **`configs/logging_utils/`**  
  Central control for log formatting and logging levels. All pipeline steps reference the same logging config, ensuring consistent logs across ingestion, transformation, and training scripts.

Together, these config folders ensure that every important parameter is discoverable, documented, and easily overridden—solidifying maintainability and clarity for both current and future collaborators.

## Chapter 3 - How Runtime Overrides Work

### Core Concept of Hydra Overrides

- **Dynamic Parameter Switching**  
  By default, `config.yaml` sets a baseline for each group (e.g., `data_versions=base`, `models=rf_optuna_trial_params`). With Hydra, you can override them at runtime. For example:

```
python universal_step.py \
  setup.script_base_name=drop_rare_drgs \
  transformations=drop_rare_drgs \
  data_versions.data_version_input=v6 \
  data_versions.data_version_output=v7
```

- **Fewer Scripts, More Flexibility**  
  Instead of writing new code for each scenario, you create or modify config files. The pipeline adjusts automatically at runtime—no duplication of logic.

### Practical Examples

#### data_versions

- **Switching Data Versions**  
  When you want to run transformations on v13 data without overwriting the existing CSV, specify:

```yaml
data_versions.data_version_input=v13
io_policy.WRITE_OUTPUT=false
```

universal_step.py detects:

```yaml
cfg.data_versions.data_version_input='v13'
cfg.data_versions.data_version_output='v13'
```

and automatically points to ./data/v13/v13.csv. Since no override changes data_version_output, it matches the input version (as defined in base.yaml). Because WRITE_OUTPUT is false, the file is not overwritten.

#### Command Line Overrides to Universal Step Function Invocation

Assume the following shell command

```
python universal_step.py \
  setup.script_base_name=drop_description_columns \
  transformations=drop_description_columns \
  data_versions.data_version_input=v1 \
  data_versions.data_version_output=v2
```

Below is the universal_step.py code snippet annotated with comments showing how each CLI override (for example, setup.script_base_name=drop_description_columns) is merged into the Hydra config and used at runtime. Refer to these comments to see precisely where and how each override affects the script’s logic and behavior.

```python
# scripts/universal_step.py
import logging

import hydra
import pandas as pd
from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.io.csv_to_dataframe import csv_to_dataframe
from dependencies.io.dataframe_to_csv import dataframe_to_csv
from dependencies.logging_utils.log_cfg_job import log_cfg_job
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.logging_utils.setup_logging import setup_logging
from dependencies.metadata.calculate_metadata import calculate_and_save_metadata
from dependencies.transformations.drop_description_columns import (
    DropDescriptionColumnsConfig,
    drop_description_columns,
)

TRANSFORMATIONS = {
    "drop_description_columns": {
        "transform": log_function_call(drop_description_columns),
        "Config": DropDescriptionColumnsConfig,
    },
    # ...
}


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def universal_step(cfg: RootConfig) -> None:
    setup_logging(cfg) # Uses setup.script_base_name for directory to write to.
    logger = logging.getLogger(__name__)

    log_cfg_job_flag = cfg.logging_utils.log_cfg_job.log_for_each_step
    if log_cfg_job_flag: # False (Default value)
        logger.info("Override: 'log_cfg_job_flag' set to %s", bool(log_cfg_job_flag))
        log_cfg_job(cfg)
    else:
        logger.debug(
            "Not logging cfg job: 'log_cfg_job_flag' == %s", bool(log_cfg_job_flag)
        )

    # Uses override `setup.script_base_name`
    transform_name = cfg.setup.script_base_name
    # Validation of passed override value for `setup.script_base_name`
    if transform_name not in TRANSFORMATIONS:
        logger.error("'%s' is not recognized in TRANSFORMATIONS.", transform_name)
        return

    # Accesses transformation function and structured config in TRANSFORMATIONS dict for key `setup.script_base_name`
    step_info = TRANSFORMATIONS[transform_name]
    # Function wrapped in log_function_call
    step_fn = step_info["transform"]
    # Dataclass config defined in the same file above the function
    step_cls = step_info["Config"]

    # All configs in group transformations have root level key == transformation name
    # cfg.transformations is override `transformations=drop_description_columns`
    step_params = cfg.transformations[transform_name]

    # In this case the default: both True
    read_input = cfg.io_policy.READ_INPUT
    write_output = cfg.io_policy.WRITE_OUTPUT

    if transform_name == "download_and_save_data": # False
        if step_cls:
            cfg_obj = step_cls(**step_params)
            step_fn(**cfg_obj.__dict__)
        else:
            step_fn()
    else:
        if read_input: # True
            # Reads v1.csv and returns DataFrame
            # Values come from config group utility_functions.csv_to_dataframe
            # Also uses data_versions.data_version_input (v1) for the actual path
            df = csv_to_dataframe(**cfg.utility_functions.csv_to_dataframe)
        else:
            df = pd.DataFrame()

        # Conditionally wrap in structured config class
        # In this example, the config is effectively empty.
        cfg_obj = step_cls(**step_params) if step_cls else None
        returned_value = step_fn(
            df,
            **(cfg_obj.__dict__ if cfg_obj else {})
        )

        if cfg.transformations.RETURNS == "df": # True
            if returned_value is not None: # True
                # Validation: Return type must either be pd.DataFrame or None
                if not isinstance(returned_value, pd.DataFrame):
                    raise TypeError(f"{transform_name} did not return a DataFrame.")
                # Return pd.DataFrame without description columns.
                df = returned_value

        if write_output: # True
            # Write pd.DataFrame to v2.csv
            # Also uses data_versions.data_version_output (v2) for the actual path
            dataframe_to_csv(df, **cfg.utility_functions.dataframe_to_csv)
            # After saving v2.csv, calculate and save metadata
            # calculate_and_save_metadata also uses data_versions.data_version_output (v2) for file paths
            calculate_and_save_metadata(
                df, **cfg.utility_functions.calculate_and_save_metadata
            )

    logger.info("Sucessfully executed step: %s", transform_name)


if __name__ == "__main__":
    # In this case we call the script directly.
    universal_step()
```

This example shows a modular “universal step” pattern where each transformation is treated as a named function and (optionally) a typed config. The script uses Hydra to retrieve CLI overrides (setup.script_base_name, transformations, data_versions, etc.) and merge them with defaults. This config is then translated into actions: a DataFrame is conditionally read (read_input), processed by the selected transformation, and conditionally written out (write_output). By delegating paths and file operations to centralized config groups (data_versions, utility_functions), it keeps I/O logic clean, consistent, and easy to override.

## Chapter 4 - Data Versioning with DVC

### Why DVC?

- **Fully Versioned Data Lineage**  
  Each transformation (drop columns, add lag features, etc.) is declared in YAML files under `configs/pipeline/`. DVC captures these pipeline stages—linking outputs (like `v10.csv`) to both the script and the previous dataset version. Anyone can restore or reproduce the exact data state used for a past model run.

- **Parallel Storage Options**  
  You can push or pull data to/from multiple remotes: an S3 bucket (for shared team access) or a local NAS (for offline or on-prem uses). Switching between them only involves adjusting DVC’s remote config.

- **Seamless Syncing**  
  Data file changes (`csv`, `json`, even large DB files) are deduplicated and stored in an efficient content-addressable way. This keeps repository size manageable while ensuring reproducibility.

- **Confidence in Production**  
  Because each data artifact is hashed and tracked, you avoid “data drift”—you’ll know exactly which rows were used to train any given model, enabling more reliable maintenance, auditing, or model retraining.

### Practical Steps

#### Quickstart Workflow

Below is a minimal workflow for pulling data, configuring your Python path, and running the DVC pipeline steps. If you rely on Kaggle data ingestion, note the optional step for using your Kaggle API key.

1. Pull Data via `dvc pull`

By default, we have a public S3 bucket configured. Simply run:

```sh
python dependencies/io/pull_dvc_s3.py
```

This fetches files into data/, configs/, and other directories (e.g., any CSV files you need).

2. Pull MLflow Artifacts

To retrieve final artifacts (e.g., model.pkl, permutation importances, etc.):

python dependencies/io/pull_mlruns_s3.py

These go into the mlruns/ folder under your project root. You can then query them using the MLflow search syntax.

(Optional) Kaggle Data Ingestion

If you need the data from Kaggle instead of S3, and have a Kaggle API key:

```sh
python scripts/universal_step.py \
    +setup.script_base_name=download_and_save_data \
    data_versions=v0  \
    io_policy.READ_INPUT=False
```

This downloads and saves data as v0 locally.

3. Run a Single Step in the Pipeline

3.1. Update cmd_python in configs/config.yaml:  
 Replace the default path ("/Users/tobias/.local/share/mamba/envs/ny/bin/python") with your interpreter’s path.

3.2. (Optional) Adjust the Pipeline  
 Modify base.yaml if you want to add or remove any pipeline stages.

3.3. Regenerate dvc.yaml  
 This rewrites the DVC pipeline commands (so they use your cmd_python path):

```sh
python dependencies/templates/generate_dvc_yaml_core.py
```

3.4. Execute the Desired Step  
For instance, if you only want to run “add lag columns on v10”:

```sh
dvc repro --force -s v10_lag_columns
```

This triggers:

```sh
python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

Hydra then loads configs/transformations/lag_columns.yaml, reads data from ./data/v10/v10.csv, and writes new data plus metadata to ./data/v11/.

4. OPTIONAL: Run All Steps

To run the entire pipeline from start to finish (potentially time-consuming):

```sh
dvc repro --force -P
```

By default, this will process every stage in dvc.yaml sequentially, generating new CSVs and metadata for each version along the way. If the Kaggle download stage is frozen, it will be skipped unless you unfreeze it in your pipeline configuration.

## Chapter 5 - Modular Code Organization

### “Dependencies” Folder

- **Reusability and Maintainability**  
  Each transformation or utility function sits in its own Python module, under folders like `dependencies/transformations/`, `dependencies/cleaning/`, `dependencies/io/`. This ensures no single script grows too large or chaotic.

- **Encapsulated Logic**  
  Functions like `lag_columns(df)`, `rolling_columns(df)`, or `drop_rare_drgs(df)` each do exactly one thing. All relevant parameters are passed from Hydra configs, so you don’t hard-code them in Python files.

- **Centralized I/O**  
  Code that handles CSV reading, writing, or metadata logging (like hashing and file-size checks) lives in `dependencies/io/`. Every pipeline stage calls these same functions, guaranteeing consistent logging and error handling across the project.

- **Logging Utilities**  
  Shared code for logging is in `dependencies/logging_utils/`. For instance, `log_function_call.py` wraps every function so you can see where it starts, where it ends, and if it fails. It centralizes logic for debugging and traceability.

- **Modeling**  
  Models and hyperparameter search methods (e.g., `rf_optuna_trial.py`, `ridge_optuna_trial.py`) reside in `dependencies/modeling/`. They all follow a similar structure, so you can easily add new algorithms (like XGBoost) without major refactoring.

### “scripts” Folder

- **Universal Entry Points**  
  The `universal_step.py` script drives any transformation or modeling step with minimal code duplication. It parses Hydra configs, reads input data, calls your chosen transformation, and writes results. You never copy-paste a script just to tweak a parameter or path.

- **Orchestration Flows**  
  Scripts like `orchestrate_dvc_flow.py` show how to chain multiple DVC stages in a single run, or how to handle advanced logic like “regenerate dvc.yaml if a stage changed.” This approach keeps high-level orchestration separate from the nitty-gritty transformation functions.

- **Low Overhead**  
  Because each script references the `dependencies/` folder for actual logic, the scripts themselves remain lean. Changing a single line in a config file can alter the behavior of the pipeline, without rewriting or branching any Python code.

This code structure ensures each piece is independently testable and easy to locate. New team members can quickly find where transformations happen, how logs are configured, and where model training logic resides, which is key to a senior-level MLOps setup.

## Chapter 6 - Example Walkthrough

### Adding Lag Columns (v10 → v11)

This walkthrough demonstrates the move from `v10.csv` to `v11.csv` by adding lag columns.

1. **configs/data_versions/v11.yaml**

   ```yaml
   # configs/data_versions/v11.yaml
   defaults:
     - base

   data_version: v11
   description: |
     Difference to v10:
     New columns get added for each listed column, shifted by 1 year (_lag1) within each [facility_id, apr_drg_code] group.
     The data is sorted on [facility_id, apr_drg_code, year].

     Adds features `_lag1` for the following columns:
     columns_to_transform = [
         "sum_discharges",
         "severity_1_portion",
         "severity_2_portion",
         "severity_3_portion",
         "severity_4_portion",
         "w_mean_charge",
         "w_mean_cost",
         "w_mean_profit",
         "w_total_mean_profit",
         "w_median_charge",
         "w_median_cost",
         "w_median_profit",
         "w_total_median_profit"
     ]
     new_cols = [f"{col}_lag1" for col in columns_to_transform]
   ```

2. **configs/transformations/lag_columns.yaml**

   ```yaml
   # configs/transformations/lag_columns.yaml
   defaults:
     - base
       - _self_

   lag_columns:
     columns_to_transform:
       - sum_discharges
       - severity_1_portion
       - severity_2_portion
       - severity_3_portion
       - severity_4_portion
       - w_mean_charge
       - w_mean_cost
       - w_mean_profit
       - w_total_mean_profit
       - w_total_mean_cost
       - w_median_charge
       - w_median_cost
       - w_median_profit
       - w_total_median_profit
       - w_total_median_cost
     groupby_time_based_cols: [facility_id, apr_drg_code, year]
     drop: true
     groupby_lag_cols: [facility_id, apr_drg_code]
     lag1_suffix: _lag1
     shift_periods: 1
   ```

3. **dependencies/transformations/lag_columns.py**

   ```python
   # dependencies/transformations/lag_columns.py
   import logging
   from dataclasses import dataclass

   import pandas as pd

   logger = logging.getLogger(__name__)


   @dataclass
   class LagColumnsConfig:
       columns_to_transform: list[str]
       groupby_time_based_cols: list[str]
       drop: bool
       groupby_lag_cols: list[str]
       lag1_suffix: str
       shift_periods: int


   def lag_columns(
       df: pd.DataFrame,
       columns_to_transform: list[str],
       groupby_time_based_cols: list[str],
       drop: bool,
       groupby_lag_cols: list[str],
       lag1_suffix: str,
       shift_periods: int,
   ) -> pd.DataFrame:
       groupby_time_based_cols = list(groupby_time_based_cols)
       groupby_lag_cols = list(groupby_lag_cols)
       drop = bool(drop)

       df = df.sort_values(by=groupby_time_based_cols).reset_index(drop=drop)

       for col in columns_to_transform:
           df[f"{col}{lag1_suffix}"] = df.groupby(groupby_lag_cols)[col].shift(
               shift_periods
           )

           logger.info("Done with core transformation: lag_columns")
       return df
   ```

4. **Runtime Command**

   ```
   python scripts/universal_step.py \
     setup.script_base_name=lag_columns \
     transformations=lag_columns \
     data_versions.data_version_input=v10 \
     data_versions.data_version_output=v11
   ```

   This tells Hydra to load `v10.yaml` for input, `v11.yaml` for output, and run the `lag_columns` transformation.

5. **Outputs**

   - A new CSV: `./data/v11/v11.csv`  
     (with columns like `sum_discharges_lag1`, `severity_1_portion_lag1`, etc.)
   - A metadata JSON: `v11_metadata.json` (row count, file hash, etc.)

6. **Why Lag Columns?**  
   This step shifts certain numeric columns by one “year” within each `[facility_id, apr_drg_code]` group. It’s a common technique for time-series or sequential analysis, letting you reference previous-year values in the current year’s modeling.

### Tying It All Together

- **Single Command, Complex Pipeline**  
  With `dvc repro --force -P`, you can re-run the entire chain from ingestion (`v0.csv`) all the way through this lag step (`v11.csv`) if the code or data changed. DVC checks each stage in `configs/pipeline/base.yaml` and executes it in order.

- **Metadata and Logging**  
  Each pipeline step calls shared logging utilities, so you can find the transformation logs in `logs/runs/<timestamp>/lag_columns.log`. Metadata JSON files confirm exactly how many rows and columns each version has and record a file hash for data integrity.

- **Experiment Management**  
  If you then run `rf_optuna_trial` on `v11.csv`, you can experiment with new features (the lag columns) and see if model metrics improve, all tracked by MLflow. Switching to a different data version or a different transformation pipeline is just another override. This flexible approach highlights how config-driven design accelerates experimentation while preserving reproducibility.

## Chapter 7 - Dynamic DVC YAML Generation

### Why Generate DVC YAML on the Fly?

- **Automatic Pipeline Updates**  
  As soon as you change or add a stage in `configs/pipeline/base.yaml`, the pipeline automatically regenerates `dvc.yaml` with the updated dependencies, commands, and outputs—no manual edits required.

- **DRY (Don’t Repeat Yourself)**  
  Instead of copying stage definitions in both Hydra configs and a static `dvc.yaml`, you maintain them in one place (`pipeline/base.yaml`). A simple template (`generate_dvc.yaml.j2`) uses the same definitions to produce a valid DVC file.

- **No Hardcoding**  
  If your Python script path, overrides, or environment variables change, you only update the Hydra config. The Jinja2 template and `generate_dvc_yaml_core.py` will ensure `dvc.yaml` always matches your latest pipeline design.

- **Full Customization**  
  Because it’s template-driven, you can easily tweak how your DVC file is formatted: add or remove sections (e.g., for metrics or checkpoints), rename `outs` to `metrics` or `plots`, etc. This is especially helpful if your pipeline expands to more advanced DVC features.

### How It Works

1. **Central Pipeline Config**  
   In `configs/pipeline/base.yaml`, each stage is declared with fields like `name`, `cmd_python`, `script`, `overrides`, `deps`, and `outs`. These fields describe exactly what DVC needs to know: how to run a stage, which inputs it depends on, and which outputs it tracks.

2. **Hydra + Omegaconf**  
   When you run something like:

   ```
   python scripts/orchestrate_dvc_flow.py pipeline=orchestrate_dvc_flow
   ```

   Hydra reads `orchestrate_dvc_flow.yaml`, merges it with your pipeline definitions in `base.yaml`, and creates one unified config. This merged config includes a list of all stages you want in `dvc.yaml`.

3. **Jinja2 Template**  
   The script `generate_dvc_yaml_core.py` loads a Jinja2 template (`generate_dvc.yaml.j2`). It iterates over the `stages` list from the Hydra config, then renders:

   ```text
   stages:
     v1_drop_description_columns:
       cmd: ...
       deps: ...
       outs: ...
   ```

   and so on for each stage. This process ensures everything in your pipeline config ends up in the final `dvc.yaml`.

4. **Flow Orchestration**  
   The logic to generate or regenerate `dvc.yaml` on demand is controlled by your Hydra config. For instance, if `skip_generation=false`, it calls `generate_dvc_yaml_core(...)`. If `allow_dvc_changes=true`, it replaces any existing `dvc.yaml` with the new one. This means you can set rules about when and how the file updates.

### Notable Advantages

- **Reduced Maintenance**  
  When adding new transformations or renaming scripts, you only modify the pipeline config. The DVC YAML automatically stays in sync, preventing errors or missing dependencies in a manually curated file.

```
python universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

- **Scalability**  
  If your pipeline doubles in size, you simply add more entries in the config. Hydra+Jinja2 will seamlessly produce the expanded `dvc.yaml` with minimal overhead, keeping the pipeline structure consistent.

- **Modular Extension**  
  You can further extend the Jinja2 template (e.g., adding a “metrics” section) or the Python script (e.g., to compare old vs. new `dvc.yaml` and only accept changes if `--allow_dvc-changes=true`). This approach is inherently flexible.

By integrating Hydra, Omegaconf, and Jinja2, you maintain a single “source of truth” for your pipeline, avoiding duplication and streamlining the entire process of DVC stage management. This is a hallmark of advanced MLOps design—where configuration, code, and data versioning all align seamlessly to reduce friction for the team.

## Chapter 8 - Flow Orchestration with Prefect

### Introduction to Prefect Flow

- **Higher-Level Pipeline Control**  
  Prefect wraps your data pipeline steps in tasks and flows, providing easier concurrency, retries, and centralized logging. This is especially useful when you have multiple pipeline triggers or want to schedule jobs more flexibly than with basic shell scripts.

- **Modular, Composable Tasks**  
  Steps like `ensure_dvc_is_clean()`, `generate_dvc_yaml()`, and `run_dvc_repro()` each become a dedicated Prefect task. Prefect then manages dependencies between tasks, handles exceptions, and logs results. You can mix these tasks with other pipelines or cloud-based orchestrations.

- **Integration With Hydra + DVC**  
  Prefect doesn’t replace Hydra or DVC; it wraps them. Hydra still manages your configuration structure, while DVC handles data versioning. Prefect’s role is orchestrating the entire end-to-end flow, ensuring each stage runs in a controlled order with proper logging.

### How the Flow Works

1. **Tasks vs. Flow**  
   In `orchestrate_dvc_flow.py`, each function—like `generate_dvc_yaml`—is annotated with `@task`. Prefect uses these to build a graph of how your pipeline executes. The `@flow` decorator then defines the higher-level sequence of tasks as one orchestrated run.

2. **Setting Environment Variables**  
   The `set_environment_vars()` task sets `HYDRA_FULL_ERROR` and `OC_CAUSE` so you get full tracebacks if something goes wrong, making debugging easier.

3. **Ensure Clean DVC State**  
   The `ensure_dvc_is_clean()` task checks for uncommitted DVC changes in `git status`. If it finds any, it raises an exception to prevent partial commits or inconsistent states.

4. **Generating the DVC YAML File**

   - If `skip_generation` is `false`, we call `generate_dvc_yaml(...)`.
   - This uses the Hydra config’s `stages_list` and a Jinja2 template to build the `dvc.yaml` automatically.
   - If the new file differs from the old one and `allow_dvc_changes` is `false`, it reverts changes for safety. Otherwise, it accepts them.

5. **Running `dvc repro`**  
   Once DVC is clean and the YAML file is up to date, `run_dvc_repro()` triggers the pipeline. You can force a re-run of all stages with `--force`, or only re-run a subset of stages (e.g., `v10_lag_columns`).

6. **Final Execution**  
   The entire process is contained in `dvc_flow(...)`. At the very end, logs are saved to a file specified by your Hydra config, and you’ll see a summary in the console. This modular design means you can schedule this flow in Prefect Cloud or run it locally with the same code.

### Why This Matters

- **Consistency**  
  Every run starts by validating DVC cleanliness and regenerating the pipeline if needed. This eliminates “accidental stale pipelines” where you forget to update `dvc.yaml`.

- **Traceability**  
  Prefect logs each task’s start/end, enabling you to see where failures occur. Combined with Hydra’s structured configs and DVC’s data versioning, you get a full audit trail of code, data, and pipeline changes.

- **Scalability**  
  For larger teams or more complex pipelines, Prefect’s concurrency, scheduling, and cloud-based run management keep things organized. You can extend the flow with additional tasks (e.g., model evaluation, MLflow artifact checks) without rewriting your entire pipeline.

By orchestrating the entire DVC pipeline with Prefect, you gain a robust control plane for your transformations. Hydra ensures configs remain DRY, DVC tracks data lineage, and Prefect coordinates execution. This layered approach is a hallmark of production-grade MLOps solutions.

## Chapter 9 - Logging and MLflow Integration

### Unified Logging Approach

- **Consistent Hydra + Python Logs**  
  The `setup_logging.py` file configures Python’s logging library to log at both DEBUG and INFO levels. Hydra directs each run’s logs into timestamped directories under `logs/runs/<date_time>`, while your pipeline’s core code writes to a “pipeline log” defined by `log_file_path` in your config.

- **Automatic Logs in Scripts**  
  In `universal_step.py`, every transformation step logs to the console and to the pipeline log. Additional debug-level messages (entering or leaving each function) come from the `@log_function_call` decorator. This level of detail makes it straightforward to diagnose issues or confirm the correct parameters are being used.

- **Central Control in `configs/logging_utils/base.yaml`**  
  You specify the log format (`%(asctime)s %(levelname)s:%(message)s`) and output paths for both Hydra runs and the pipeline in a single place. This ensures every pipeline step, model training, or data transformation follows the same conventions.

### Traceability with MLflow

- **Model Artifact Storage**  
  Both `rf_optuna_trial.py` and `ridge_optuna_trial.py` log final models as artifacts in `./mlruns/`. MLflow also stores metrics (like RMSE, R2) and parameters (e.g., random forest hyperparameters). You can examine them locally with `mlflow ui` or push them to a remote S3-based MLflow server.

- **Permutation Importances**  
  During the final model run, each script calls `calculate_and_log_importances_as_artifact(...)` to compute permutation-based feature importances. These are persisted as CSV artifacts in MLflow, letting you compare the top features across multiple runs or model variants.

- **Experiment Consistency**  
  Hydra merges your experiment configuration (train/val/test splits, random seeds) with the model parameters. MLflow records these details automatically once you log them in the script. This means you can reconstruct exactly how each experiment was done—even months later—by referencing the logged parameters and your pipeline’s DVC version.

### Pipeline Log Example

Below is part of the pipeline log showing each stage run sequentially (e.g., `v0_download_and_save_data`, `v0_sanitize_column_names`), including how metadata is calculated and saved. It highlights:

- **Stage Execution**  
  Each DVC stage prints a “Running stage” message. Hydra overrides (e.g., `setup.script_base_name=download_and_save_data`) appear in the command, indicating which transformation or step is being executed.

- **File I/O and Metadata**  
  The pipeline logs read/write operations along with file hashes. For example:

  ```
  [2025-03-21 16:38:05,393][dependencies.metadata.calculate_metadata][INFO] - Metadata successfully saved to /Users/tobias/...
  ```

  This ensures you can track each version of your data artifacts.

- **MLflow Logging**  
  Whenever you run `rf_optuna_trial` or `ridge_optuna_trial`, MLflow logs appear in the same pipeline log. You see trial metrics, best hyperparameters, and the final model logging.

- **Timestamps and Order**  
  Each log entry is timestamped, so you know exactly when each step starts and finishes. This is crucial for debugging (e.g., if a step took unexpectedly long) or verifying that all transformations happened in the correct sequence.

By combining Hydra, Python logging, and MLflow experiment tracking, you get a comprehensive picture of what ran, when it ran, how it was configured, which data version was used, and how the model performed—all in one place. This makes the entire system highly auditable and easier to maintain at scale.

## Chapter 10 - Conclusion and Further Steps

### Conclusion and Future Directions

#### 10.1 Conclusion

This project demonstrates a comprehensive data-to-model pipeline, from ingestion and cleaning to hyperparameter tuning and final model logging. By integrating Hydra, DVC, and MLflow—and later orchestrating them with Prefect—we solve real problems like:

- **Data Drift** (DVC ensures exact data lineage)
- **Configuration Drift** (Hydra’s single source of truth)
- **Experiment Tracking** (MLflow logs all parameters and artifacts)
- **Reproducible Pipelines** (DVC + Hydra define each stage consistently)
- **Team Scalability** (code is modular, transformations are pluggable)

These approaches highlight a deeper MLOps mindset: one that ensures every experiment can be reproduced, audited, and improved without guesswork. While this codebase focuses primarily on local pipelines, advanced versioning, and experiment tracking, it can easily extend to containerization (Docker), orchestration on cloud platforms (AWS, GCP), or robust CI/CD testing—areas I’m well-versed in but kept out of scope here to spotlight the data+model pipeline itself.

#### 10.2 Additional Tools Not Shown Here

- **Containerization**  
  Dockerizing each step or microservice is straightforward. Combining these containers with Kubernetes or ECS ensures the pipeline scales with demand and offers easy rollback in production.

- **CI/CD and Testing**  
  Tools like GitHub Actions or Jenkins can run automated tests after each commit. For data testing, we’d incorporate Great Expectations or unit tests that validate transformations. This guarantees new code or data doesn’t break existing workflows.

- **Infrastructure as Code (IaC)**  
  Provisioning AWS S3 buckets, EC2 instances, or EKS clusters via Terraform or CloudFormation. This practice ensures the entire infrastructure is version-controlled and easily replicable across dev, staging, and prod environments.

#### 10.3 Why This Project Stands Out

Many MLOps pipelines exist, but they often miss:

- **Strict reproducibility** across transformations
- **Unified config management** that prevents duplication
- **Built-in experiment logging** with minimal overhead
- **Seamless extension** to new data versions or model architectures

This project tackles each of these challenges head-on. Every piece—Hydra configs, DVC pipelines, MLflow logging, Prefect orchestration—is carefully interwoven so teams can quickly iterate on data, transformations, and models without losing track of changes.

#### 10.4 Aiming for Senior-Level MLOps Roles

My goal in building this pipeline was not just to showcase programming, but to demonstrate the ability to design, maintain, and evolve complex ML systems. Senior MLOps engineers must:

- Spot critical bottlenecks (data drift, pipeline fragmentation).
- Enforce best practices (version control, config management, logging).
- Align these solutions with real-world constraints (cloud costs, compute resources, team structure).

This project reflects those priorities, solving the pains that plague many data science teams—lack of clarity in configuration, ad-hoc scripts, and confusion over which data was used for which model. By emphasizing standardization, reproducibility, and easy collaboration, it provides a blueprint for stable, production-grade pipelines.

#### 10.5 Where to Go Next

- **Cloud Deployments**  
  Containerizing each step, hooking the pipeline to AWS or GCP, and automating triggers with something like Lambda or Cloud Functions for a fully managed solution.

- **Automated Testing**  
  Incorporating continuous integration pipelines that test transformations and data validity as soon as code is pushed.

- **Further Experimentation**  
  Integrating more advanced parameter search methods (Bayesian or multi-objective Optuna) or diverse model classes (e.g., XGBoost, LightGBM).

- **Monitoring & Alerting**  
  Tools like Prometheus or Grafana can track model metrics post-deployment, enabling real-time alerts if performance degrades.

#### 10.6 Final Thoughts

By focusing on one cohesive pipeline, I’ve shown how to unite configuration management, data versioning, experiment tracking, and orchestration into a powerful, maintainable system. This is just one slice of my broader skill set; in a real-world setting, I’d also layer on robust testing, containers, IaC, and multi-cloud considerations.

If you’re looking to hire an engineer who not only writes code but also implements the architectural principles needed for long-term success in ML projects, this pipeline is an example of what I bring to the table—clean, scalable, and thoroughly documented MLOps solutions. Let’s talk about how I can help transform your data science workflows into a repeatable, production-grade machine learning platform.
