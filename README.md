<!--README.md-->
# Medical DRG in NY — A Reproducible ML Pipeline

This repository contains a fully reproducible, config-driven pipeline for analyzing New York State hospital DRG (Diagnosis-Related Group) data. It uses Hydra (for hierarchical configs), DVC (for data versioning & reproducibility), and MLflow (for experiment tracking). The primary goal is to showcase senior-level MLOps patterns: modular transformations, data lineage, and hyperparameter optimization with minimal code duplication.

## Key Features

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

1. Install Dependencies

```sh
# Create a conda environment from env.yaml
conda env create -f env.yaml
conda activate ny
```

2. Pull Data via DVC (if you have a remote):

```sh
dvc pull
```

Or run ingestion for v0 if you rely on Kaggle:

```sh
python scripts/universal_step.py \
    +setup.script_base_name=download_and_save_data \
    data_versions=v0  \
    io_policy.READ_INPUT=False
```

3. Run the Entire Pipeline

```sh
dvc repro --force -P
```

This executes each stage in configs/pipeline/base.yaml sequentially, producing new CSV files (and metadata) for each data version.

4. Run a Single Transformation in dvc.yaml (example: add lag columns on v10)

```sh
dvc repro --force -s v10_lag_columns
```

The above code executes the following:

```sh
python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

Hydra will load configs/transformations/lag_columns.yaml, v10 data as input, and produce v11 data.
- Input data is loaded from [./data/v10/v10.csv](/data/v10/v10.csv)
- Output data v11 is written to [./data/v11/v11.csv](/data/v11/v11.csv)
- Output data v11's metadata is written to [./data/v11/v11_metadata.json](/data/v11/v11_metadata.json)

5. Check Logs

Logs are saved under `logs/runs/${now:%Y-%m-%d_%H-%M-%S}/${setup.script_base_name}` (see details under [Logging Configuration](#logging-configuration))

For this run: [./logs/runs/2025-03-20_17-30-59/lag_columns.log](logs/runs/2025-03-20_17-30-59/lag_columns.log)

```log
Running stage 'v10_lag_columns':
> /Users/tobias/.local/share/mamba/envs/practice/bin/python /Users/tobias/.local/projects/portfolio_medical_drg_ny/scripts/universal_step.py setup.script_base_name=lag_columns transformations=lag_columns data_versions.data_version_input=v10 data_versions.data_version_output=v11
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
[2025-03-20 17:31:12,279][__main__][INFO] - Sucessfully executed step: lag_columns
Updating lock file 'dvc.lock'
Use `dvc push` to send your updates to remote storage.
```

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

⸻

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
