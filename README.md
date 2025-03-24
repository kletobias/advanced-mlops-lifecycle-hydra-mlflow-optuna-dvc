<!--README.md-->
# Medical DRG in NY — A Reproducible ML Pipeline

This repository contains a fully reproducible, config-driven pipeline for analyzing New York State hospital DRG (Diagnosis-Related Group) data. It uses Hydra (for hierarchical configs), DVC (for data versioning & reproducibility), and MLflow (for experiment tracking). The primary goal is to showcase senior-level MLOps patterns: modular transformations, data lineage, and hyperparameter optimization with minimal code duplication.

## Key Features

MLOps: End-to-end Pipeline management

- Hydra Configuration
    All parameters (data paths, transformations, hyperparameters) are separated from the code. Simply override them at runtime to switch between data versions (e.g., v0, v1, …) or transformations (lag_columns, drop_rare_drgs, etc.).

- Data Versioning with DVC
    Each pipeline stage (e.g. ingestion, transformation, modeling) is represented in configs/pipeline/base.yaml. DVC tracks these transformations, ensuring every data version is reproducible.

- Experiment Tracking with MLflow
    Scripts like rf_optuna_trial.py or ridge_optuna_trial.py log metrics and artifacts (model pickle, permutation importances) to MLflow, enabling easy model comparison.

- Modular Transformations
    Each transformation is a small, testable function in dependencies/transformations/. Configuration (which columns to shift, thresholds to drop DRGs, etc.) lives in matching YAML files under configs/transformations/.

- Metadata Logging
    Every time you generate a new CSV, the code saves a JSON metadata file (row count, column types, file hash, etc.) for reproducibility.


## Repository Structure (High-Level)

```
.
├── configs/                # All Hydra config files
│   ├── config.yaml         # Main entry point (merges other config groups)
│   ├── data_versions/      # Each version of the dataset (v0, v1, ...)
│   ├── pipeline/           # DVC pipeline definitions
│   ├── transformations/    # YAML settings for each transformation
│   └── ... (logging_utils, ml_experiments, etc.)
├── data/                   # Data folder (versioned by DVC)
├── dependencies/           # Modular code for transformations, ingestion, modeling, etc.
│   ├── transformations/    # Each transformation is a function + config schema
│   ├── modeling/           # ML/hyperparameter scripts (Optuna, MLflow)
│   └── ...
├── scripts/
│   ├── universal_step.py   # "One script to rule them all" - runs any transformation
│   └── orchestrate_dvc_flow.py  # Prefect + DVC orchestration script
├── logs/                   # Pipeline logs (auto-generated)
├── dvc.yaml                # Will be generated or updated via DVC (pipeline)
├── README.md               # You're reading it
└── ...
```

## Quickstart

Below is a minimal way to get up and running.

### 1. Install Dependencies

> **All the following commands assume that you have completed this step and that you have activated the `ny` environment (or whatever you name it).**

**With Conda**

```sh
# Create a conda environment from env.yaml
conda env create -f env.yaml
conda activate ny
```

With Micromamba:

```sh
# Create a conda environment from env.yaml
micromamba env create -f env.yaml
micromamba activate ny
```

Environment creation is only tested on Mac ARM64 architecture using micromamba 2.0.7, Python 3.12.9.

In case of problems, a workaround is pinning Python 3.11, and installing as you go.

If environment creation fails on Linux x86_64:

```sh
conda config --add channels conda-forge
conda config --add channels defaults
conda config --set channel_priority flexible
conda install -n base -c conda-forge mamba
mamba env create -f env.yaml
mamba activate ny
```

---

### 2. Pull Data via dvc pull from Our S3 Bucket

> IMPORTANT: Make sure you have dvc-s3 installed first.

By default, our pipeline is configured to use data from a public S3 bucket. The script below sets up the remote DVC configuration if needed, then pulls the dataset:

```sh
# Outputs will populate data/, configs/, etc.
python dependencies/io/pull_dvc_s3.py
```

---

### 3. Pull the Entire mlruns Folder from S3

> IMPORTANT: This step is also critical.

By pulling the mlruns folder, you’ll retrieve final artifacts, including permutation importances, RandomForestRegressor importances, model .pkl files, and so on. You can explore them locally using MLflow’s query syntax (e.g., “search runs” or “view artifacts”). Any new Optuna trials you run will automatically log to the same mlruns folder—no extra configuration needed.

```sh
# This populates `mlruns/` in your project root.
python dependencies/io/pull_mlruns_s3.py
```

(Optional) Ingestion for Data Version v0 via Kaggle

Requires a Kaggle API key.

If you want to reproduce the original ingestion logic (instead of pulling data from S3), run:

```sh
python scripts/universal_step.py \
    +setup.script_base_name=download_and_save_data \
    data_versions=v0 \
    io_policy.READ_INPUT=False
```

We typically rely on the S3-hosted data to avoid Kaggle dependencies. If you do want to replicate Kaggle ingestion, uncomment the step in your pipeline config or run it directly.

⸻

### 4. Run the Entire Pipeline

Check out configs/pipeline/base.yaml to see each transformation stage in sequence.
After pulling data from S3, DVC will often detect no changes (i.e., everything is up to date). If you want to force all stages to run anyway:

```sh
dvc repro --force -P
```

- `--force`: Tells DVC to re-run stages even if they appear up to date.
- `-P` (pipeline mode): Executes all stages topologically, from start to finish (no parallel branches).

Without --force, you’d likely see "Data and pipelines are up to date", since pulling from S3 leaves no further changes for DVC to process.

---

### 5. Run a Single Transformation (Example: Add Lag Columns on v10)

To run only the v10_lag_columns stage:

```sh
dvc repro --force -s v10_lag_columns
```

- We still use `--force` so DVC re-runs the stage, ignoring any checks about freshness.
- No `-P` here, because we’re not executing the entire pipeline—just one stage.

The command above is equivalent to manually calling:

```sh
python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

Hydra loads configs/transformations/lag_columns.yaml to take v10 data as input and produce v11 data:
- Input: ./data/v10/v10.csv
- Output: ./data/v11/v11.csv
- Metadata: ./data/v11/v11_metadata.json

---

### 6. Check Logs

Logs are saved under `logs/runs/${now:%Y-%m-%d_%H-%M-%S}/${setup.script_base_name}` (see Logging Configuration for details).

Example:
./logs/runs/2025-03-20_17-30-59/lag_columns.log

<details>
<summary>Sample Log Output</summary>

```sh
Running stage 'v10_lag_columns':
> /Users/tobias/.local/share/mamba/envs/practice/bin/python /Users/tobias/.local/projects/portfolio_medical_drg_ny/scripts/universal_step.py setup.script_base_name=lag_columns transformations=lag_columns data_versions=v10 data_versions=v11
[2025-03-20 17:30:59,271][dependencies.general.mkdir_if_not_exists][INFO] - Directory exists, skipping creation
/Users/tobias/.local/projects/portfolio_medical_drg_ny/logs/pipeline
[2025-03-20 17:30:59,838][dependencies.io.csv_to_dataframe][INFO] - Read /Users/tobias/.local/projects/portfolio_medical_drg_ny/data/v10/v10.csv, created df
[2025-03-20 17:31:00,008][dependencies.transformations.lag_columns][INFO] - Done with core transformation: lag_columns
[2025-03-20 17:31:00,010][dependencies.general.mkdir_if_not_exists][INFO] - Directory exists, skipping creation
/Users/tobias/.local/projects/portfolio_medical_drg_ny/data/v11
[2025-03-20 17:31:05,964][dependencies.io.dataframe_to_csv][INFO] - Exported df to csv using filepath: /Users/tobias/.local/projects/portfolio_medical_drg_ny/data/v11/v11.csv
[2025-03-20 17:31:12,048][dependencies.metadata.compute_file_hash][INFO] - Generated file hash: 85b89b3126ee6cfa18ad5fc716081f6baad1a3abf3470cd505ff588309c1c30e
[2025-03-20 17:31:12,278][dependencies.metadata.calculate_metadata][INFO] - Generated metadata for file: /Users/tobias/.local/projects/portfolio_medical_drg_ny/data/v11/v11.csv
[2025-03-20 17:31:12,279][dependencies.metadata.calculate_metadata][INFO] - Metadata successfully saved to /Users/tobias/.local/projects/portfolio_medical_drg_ny/data/v11/v11_metadata.json
[2025-03-20 17:31:12,279][__main__][INFO] - Successfully executed step: lag_columns
Updating lock file 'dvc.lock'
Use `dvc push` to send your updates to remote storage.
```

</details>


Check these logs to confirm data was read, transformations ran, CSV outputs were saved, and metadata was generated.

---

### Why We Use --force -P for the Entire Pipeline

After pulling data from S3, DVC sees no changes to the code or data, so dvc repro normally skips everything.
By adding `--force -P`, you ensure all pipeline stages run anyway, in topological order:
- `--force`: Re-runs stages that might otherwise appear up to date.
- `-P`: Tells DVC to run the pipeline from first to last (rather than just re-running single stages or skipping branches).

Why We Use `--force` (But Not `-P`) for a Single Stage

When you only want to re-run one stage (e.g., v10_lag_columns), you can do:

```sh
dvc repro --force -s v10_lag_columns
```

You still use `--force` to avoid the “Data and pipelines are up to date” message, but you don’t need `-P` because you’re not executing the entire pipeline—just that one stage.

---

By following these steps and explanations, you can fully reproduce or re-run any portion of the pipeline—whether it’s a single transformation or the entire chain—even if the original data is already up to date.

### Logging Configuration

In the example above we executed transformation `lag_columns`. The override `setup.script_base_name=lag_columns` is used to define where the logs for this transformation are written to.

```sh
python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

We use hydra's logger if it exists in our execution of [setup_logging.py](dependencies/logging_utils/setup_logging.py), together with our [log_function_call.py](dependencies/logging_utils/log_function_call.py) in the [universal_step.py](scripts/universal_step.py), and our [log_function_call.py](dependencies/logging_utils/log_function_call.py)

```yaml
# configs/hydra/base.yaml
job:
  name: ${setup.script_base_name} # In the example: lag_columns
run:
  dir: logs/runs/${now:%Y-%m-%d_%H-%M-%S}
sweep:
  dir: logs/multiruns/${now:%Y-%m-%d_%H-%M-%S}
  subdir: ${hydra.job.num}
```

In this example the log is saved under:

(logs/runs/2025-03-20_17-39-23/lag_columns.log)[logs/runs/2025-03-20_17-39-23/lag_columns.log]

## Running ML Experiments

We use MLflow and Optuna for hyperparameter tuning:
	•	Random Forest:

python scripts/universal_step.py \
  +setup.script_base_name=rf_optuna_trial \
  data_versions=v13 \
  model_params=rf_optuna_trial_params


	•	Ridge Regression:

python scripts/universal_step.py \
  +setup.script_base_name=ridge_optuna_trial \
  data_versions=v13 \
  model_params=ridge_optuna_trial_params



Each trial logs metrics (like RMSE, R²) and artifacts to ./mlruns by default.

#### Example: Permutation Importances logged as Artifact

The universal importance metric we use is permutation importances

```csv
feature,importances
w_total_median_profit_lag1,0.10964554607356722
w_total_mean_profit_lag1,0.10563058193740327
w_total_median_profit_rolling2,0.08264136737424133
w_total_mean_profit_rolling2,0.055836704844702115
w_total_mean_cost_rolling2,0.013683989835306897
w_total_mean_cost_lag1,0.010790000561158775
w_total_median_cost_rolling2,0.009244236750888502
w_total_median_cost_lag1,0.00867279031657484
sum_discharges_rolling2,0.0026856946195632724
sum_discharges_lag1,0.0025191493380667617
...
```

#### Example: RandomForestRegressor Importances logged as Artifact

`rf_optuna_trial.py` takes advantage of the fact that there is another feature importances metric native to the RandomForest estimator. It logs that as well.

```csv
feature,importance
w_total_median_profit_lag1,0.2170874864655451
w_total_mean_profit_lag1,0.20730719583731547
w_total_median_profit_rolling2,0.20122115990233386
w_total_mean_profit_rolling2,0.1522267096323898
w_total_mean_cost_rolling2,0.059487923298292424
w_total_mean_cost_lag1,0.047090312814948604
w_total_median_cost_rolling2,0.034416037187213325
w_total_median_cost_lag1,0.029658001263519133
sum_discharges_lag1,0.010165206374812752
sum_discharges_rolling2,0.009809536146385413
...
```

#### Example: Prefect logs from an entire pipeline run

```sh
(ny) ~ $ python scripts/orchestrate_dvc_flow.py pipeline=orchestrate_dvc_flo
run=true pipeline.pipeline_run=true logging_utils.level=20
[2025-03-21 16:37:51,456][dependencies.general.mkdir_if_not_exists][INFO] - 
/Users/tobias/.local/projects/portfolio_medical_drg_ny/logs/pipeline
[2025-03-21 16:37:51,456][root][INFO] - Reading config, validating user stag
[2025-03-21 16:37:51,456][root][INFO] - User stages valid
16:37:51.854 | INFO    | prefect.engine - Created flow run 'horned-shellfish
16:37:51.876 | INFO    | Flow run 'horned-shellfish' - Flow start
16:37:51.899 | INFO    | Flow run 'horned-shellfish' - Created task run 'set
16:37:51.900 | INFO    | Flow run 'horned-shellfish' - Executing 'set_enviro
16:37:51.925 | INFO    | Task run 'set_environment_vars-0' - Setting environ
16:37:51.938 | INFO    | Task run 'set_environment_vars-0' - Finished in sta
16:37:51.967 | INFO    | Flow run 'horned-shellfish' - Created task run 'ens
16:37:51.968 | INFO    | Flow run 'horned-shellfish' - Executing 'ensure_dvc
16:37:51.991 | INFO    | Task run 'ensure_dvc_is_clean-0' - Checking for unc
16:37:52.006 | INFO    | Task run 'ensure_dvc_is_clean-0' - No uncommitted D
16:37:52.023 | INFO    | Task run 'ensure_dvc_is_clean-0' - Finished in stat
16:37:52.037 | INFO    | Flow run 'horned-shellfish' - Created task run 'gen
16:37:52.038 | INFO    | Flow run 'horned-shellfish' - Executing 'generate_d
16:37:52.062 | INFO    | Task run 'generate_dvc_yaml-0' - Attempting to gene
16:37:52.063 | INFO    | Task run 'generate_dvc_yaml-0' - Backing up existin
16:37:52.083 | INFO    | Task run 'generate_dvc_yaml-0' - No differences det
16:37:52.096 | INFO    | Task run 'generate_dvc_yaml-0' - Finished in state 
16:37:52.108 | INFO    | Flow run 'horned-shellfish' - Created task run 'run
16:37:52.109 | INFO    | Flow run 'horned-shellfish' - Executing 'run_dvc_re
16:37:52.134 | INFO    | Task run 'run_dvc_repro-0' - Running DVC repro
16:37:52.134 | INFO    | Task run 'run_dvc_repro-0' - Pipeline mode is ON
16:37:52.134 | INFO    | Task run 'run_dvc_repro-0' - Force mode is ON
16:37:52.135 | INFO    | Task run 'run_dvc_repro-0' - No specific stages => 
17:52:48.384 | INFO    | Task run 'run_dvc_repro-0' - Finished in state Completed()
17:52:48.385 | INFO    | Flow run 'horned-shellfish' - Flow done
17:52:48.407 | INFO    | Flow run 'horned-shellfish' - Finished in state Completed('All states completed.')
```

## Highlights and Why It’s Not “Just Scripts”
	1.	Config-Driven: Hydra decouples parameters from code. No rewriting CSV paths or columns.
	2.	Fully Versioned: DVC ensures each step from v0 to v13 is reproducible.
	3.	Scalable: Add new transformations by creating a .py in dependencies/transformations/ plus a .yaml in configs/transformations/.
	4.	Testable: Each transformation is a small function with typed configs, making it easier to test.
	5.	Production Mindset: Logging, metadata, MLflow integration, and potential CI/CD hooks.

⸻

## Further Documentation
	•	For a deep dive on each transformation, data version, and design rationale, see Detailed Docs (placeholder link) or the docs/ folder.
	•	For a high-level conceptual overview or if you’re just browsing, check out:
	•	Hydra
	•	DVC
	•	MLflow

⸻

## License and Contact
	•	License: MIT (or your chosen license).
	•	Author: Your Name — feel free to connect!
	•	Contact: Open an issue on GitHub or message me on LinkedIn for questions.

⸻

Thank you for checking out this project! If you have any questions or want to see how a full MLOps pipeline can be scaled further, reach out via GitHub issues or LinkedIn.
