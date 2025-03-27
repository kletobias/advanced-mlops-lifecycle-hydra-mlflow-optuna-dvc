<!--README.md-->
# Medical DRG in NY — A Reproducible ML Pipeline

This repository contains a fully reproducible, config-driven pipeline for analyzing New York State hospital DRG (Diagnosis-Related Group) data. It uses Hydra (for hierarchical configs), DVC (for data versioning & reproducibility), and MLflow (for experiment tracking). The primary goal is to showcase senior-level MLOps patterns: modular transformations, data lineage, and hyperparameter optimization with minimal code duplication.

---

## Key Features

- **Hydra Configuration**  
  All parameters (data paths, transformations, hyperparameters) are separated from the code. Simply override them at runtime to switch between data versions (e.g., `v0`, `v1`, etc.) or transformations (`lag_columns`, `drop_rare_drgs`, etc.).

- **Data Versioning with DVC**  
  Each pipeline stage (e.g., ingestion, transformation, modeling) is represented in `configs/pipeline/base.yaml`. DVC tracks these transformations, ensuring that every data version is reproducible.

- **Experiment Tracking with MLflow**  
  Scripts like `rf_optuna_trial.py` or `ridge_optuna_trial.py` log metrics and artifacts (model pickle, permutation importances) to MLflow, making it easy to compare experiments.

- **Modular Transformations**  
  Each transformation is a small, testable function in `dependencies/transformations/`. Configuration (columns to shift, thresholds to drop DRGs, etc.) lives in matching YAML files under `configs/transformations/`.

- **Metadata Logging**  
  Every time you generate a new CSV, the code saves a JSON metadata file (row count, column types, file hash, etc.) for reproducibility.

---

## Repository Structure (High-Level)
```
.
├── configs/                # All Hydra config files
│   ├── config.yaml         # Main entry point (merges other config groups)
│   ├── data_versions/      # Each version of the dataset (v0, v1, …)
│   ├── pipeline/           # DVC pipeline definitions
│   ├── transformations/    # YAML settings for each transformation
│   └── … (logging_utils, ml_experiments, etc.)
├── data/                   # Data folder (versioned by DVC)
├── dependencies/           # Modular code for transformations, ingestion, modeling, etc.
│   ├── transformations/    # Each transformation is a function + config schema
│   ├── modeling/           # ML/hyperparameter scripts (Optuna, MLflow)
│   └── …
├── scripts/
│   ├── universal_step.py   # “One script to rule them all” - runs any transformation
│   └── orchestrate_dvc_flow.py  # Prefect + DVC orchestration script
├── logs/                   # Pipeline logs (auto-generated)
├── dvc.yaml                # Will be generated or updated via DVC (pipeline)
├── README.md               # You’re reading it
└── …
```
---

## Quickstart

Below is a minimal way to get set up and run the pipeline. Make sure your Python interpreter is available; if you are creating a conda/micromamba environment, you can install dependencies from `env.yaml` and then update `cmd_python` in your config before running DVC.

### 1. Install Dependencies

Create (and activate) your environment using conda or micromamba:

```sh
# Using Conda:
conda env create -f env.yaml
conda activate ny
```

```sh
# Using Micromamba:
micromamba env create -f env.yaml
micromamba activate ny
```

⸻

### 2. Pull Data via dvc pull from Our Public S3 Bucket

Everything is pre-configured to pull from a public S3 bucket (read-only). If needed, set it as a new remote:

```sh
python dependencies/io/pull_dvc_s3.py
```

This step populates your local data/, configs/, etc.

⸻

### 3. Pull the Entire mlruns Folder from Our S3 Bucket

Retrieve final artifacts (model pickle, importances, etc.):

```sh
python dependencies/io/pull_mlruns_s3.py
```

They are stored in the mlruns/ folder, so you can query them using MLflow’s search syntax.

Optional: If you rely on Kaggle data ingestion, you’ll need a Kaggle API key. Example:

```sh
python scripts/universal_step.py \
    +setup.script_base_name=download_and_save_data \
    data_versions=v0  \
    io_policy.READ_INPUT=False
```

⸻

### 4. Run a Single Step in the Pipeline

1. Update cmd_python in configs/config.yaml:  
  Enter the path to your Python interpreter (instead of "/Users/tobias/.local/share/mamba/envs/ny/bin/python").
2. (Optional) Edit Pipeline Stages  
  If you want to modify the flow, open configs/pipeline/base.yaml.
3. Regenerate dvc.yaml  
This ensures your Python interpreter path is reflected in the pipeline commands:

```sh
python dependencies/templates/generate_dvc_yaml_core.py
```

### 5. Run All Steps or a Single One

- All Steps:

```sh
dvc repro --force -P
```

Potentially time-consuming—rebuilds each stage.


- Single Step (e.g., v10_lag_columns):

```sh
dvc repro --force -s v10_lag_columns
```

This runs:

```sh
python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
```

Hydra loads configs/transformations/lag_columns.yaml, reads from ./data/v10/v10.csv, and writes new data (with metadata) to ./data/v11.

⸻

### 5. Logs and Pipeline Output

Logs are stored under:

```txt
logs/runs/${now:%Y-%m-%d_%H-%M-%S}/${setup.script_base_name}
```

For instance, running the lag_columns step might produce:

```txt
logs/runs/2025-03-20_17-30-59/lag_columns.log
```

with details about CSV paths, metadata, and transformation execution.

⸻

## Running ML Experiments

This repo integrates MLflow and Optuna for hyperparameter tuning. For example, to run a Random Forest trial:

```sh
python scripts/universal_step.py \
  setup.script_base_name=rf_optuna_trial \
  data_versions=v13 \
  model_params=rf_optuna_trial_params
```

A similar approach applies to Ridge Regression or other models. Each run logs metrics (RMSE, R², etc.) and artifacts (importances, pickled model) to ./mlruns.

⸻

Example Artifacts: Permutation Importances

```csv
feature,importances
w_total_median_profit_lag1,0.10964554607356722
w_total_mean_profit_lag1,0.10563058193740327
...
```

Example Artifacts: RandomForestRegressor Importances

```csv
feature,importance
w_total_median_profit_lag1,0.2170874864655451
w_total_mean_profit_lag1,0.20730719583731547
...
```

⸻

Highlights and Why It’s Not “Just Scripts”
1. Config-Driven: Hydra decouples parameters from code. No rewriting CSV paths or hyperparams.
2. Fully Versioned: DVC ensures each step (v0 to v13) is reproducible.
3. Scalable: Add new transformations by creating a .py in dependencies/transformations/ plus a .yaml in configs/transformations/.
4. Testable: Each transformation is a small function with typed configs, making it easier to test.
5. Production Mindset: Integrated logging, metadata, MLflow, and potential CI/CD hooks.

⸻

Further Documentation
- Detailed Docs: See the docs/ folder (placeholder) for a deeper look at each transformation, data version, and design rationale.
- Hydra: Hydra documentation
- DVC: DVC documentation
- MLflow: MLflow documentation

⸻

**Contact**  
- Author: Tobias Klein
- Contact:
    - Open an issue on GitHub or message me on LinkedIn for questions.
    - [LinkedIn](https://www.linkedin.com/in/deep-learning-mastery/)
    - [Website](https://deep-learning-mastery.com/)

Thank you for exploring this project! For more information on scaling or productionizing an MLOps pipeline, reach out via GitHub issues or LinkedIn.

© 2025 Tobias Klein. All rights reserved.

This repository is provided solely for demonstration and personal review. No license is granted for commercial or non-commercial use, copying, modification, or distribution without explicit, written permission from the author.
