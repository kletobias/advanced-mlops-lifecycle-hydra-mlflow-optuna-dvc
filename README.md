<!--README.md-->
# Medical DRG in NY — A Reproducible ML Pipeline

This repository contains a config-driven pipeline for analyzing New York State hospital DRG (Diagnosis-Related Group) data. It uses **Hydra** for hierarchical configs, **DVC** for data versioning & reproducibility, and **MLflow** for experiment tracking. The main goal is to showcase advanced MLOps patterns—such as modular transformations, data lineage, and hyperparameter optimization—at a senior engineering level.


> **Note**: This repo is primarily a _portfolio project_. The pipeline is mostly reproducible, but may require a few **manual adjustments** to run end-to-end on your machine (explained below). If you just want to inspect the pipeline structure and ML artifacts, you can do so without running the entire pipeline locally.

---

## Dataset

- Name: 2010 New York State Hospital Inpatient Discharge Data
- Info Kaggle: [2010 New York State Hospital Inpatient Discharge Data](https://www.kaggle.com/datasets/thedevastator/2010-new-york-state-hospital-inpatient-discharge)
- Source: [data.world](https://data.world/healthdatany) (Requires login)

## Key Features

- **Hydra Configuration**  
  All parameters (paths, transformations, hyperparameters) are separated from the code, making it easy to customize or switch data versions.

- **Data Versioning with DVC**  
  Each pipeline stage (e.g., ingestion, transformation, modeling) is declared in YAML configs. DVC ensures the transformations are reproducible, tracking large artifacts outside of Git.

- **Experiment Tracking with MLflow**  
  Model metrics and artifacts (e.g., pickled model, permutation importances) are automatically logged, so you can compare runs.

- **Modular Transformations**  
  Every transformation is a small function with its own YAML config. That means you can easily plug in or remove steps.

- **Metadata Logging**  
  Each time you generate a new CSV, a JSON metadata file is produced (row count, column types, file hash, etc.) for thorough lineage.

---

## Repository Structure

```
.
├── configs/                # Hydra config files
│   ├── config.yaml         # Main Hydra entry point
│   ├── data_versions/      # Each data version (v0, v1, etc.)
│   ├── pipeline/           # Pipeline definitions (for DVC)
│   ├── transformations/    # YAML settings per transformation
│   └── …
├── data/                   # Versioned by DVC (not all included in Git)
├── dependencies/           # Common code: transformations, modeling, etc.
│   ├── transformations/
│   ├── modeling/
│   └── …
├── scripts/
│   ├── universal_step.py   # A single script that can run any transformation
│   └── orchestrate_dvc_flow.py  # Prefect + DVC orchestration example
├── logs/                   # Pipeline logs
├── dvc.yaml                # Master pipeline (tracked in Git)
├── README.md               # You’re reading it
└── …
```

### Additional Docs

- See [documentation/detailed_documentation.md](documentation/detailed_documentation.md) for a deeper dive into transformations, pipeline orchestration, etc.
- Hydra: [Hydra docs](https://hydra.cc/docs/intro/)
- DVC: [DVC docs](https://dvc.org/doc)
- MLflow: [MLflow docs](https://mlflow.org/docs/latest)

---

## Check the Logs

If you want to get a better idea of the pipline, check out the logs below:

A complete pipeline log from running `scripts/orchestrate_dvc_flow.py` is available in the `logs/pipeline` directory: [pipeline log directory](logs/pipeline).

Hydra logs from the same execution, with one file per transformation, are located in `logs/runs`: [runs logs directory](logs/runs/).

## Installation & Basic Setup

> **Disclaimer**: The instructions below assume you’re familiar with DVC, Hydra, and basic Python package management. Because this is a portfolio repo, you may need to tweak some paths in `configs/` or environment variables to get everything running on your setup.

### 1. Create & Activate a Python Environment

```bash
conda env create -f env.yaml
conda activate ny
```

or

```bash
micromamba env create -f env.yaml
micromamba activate ny
```

### 2. (Optional) Set Environment Variables

Some Hydra configs reference environment variables like `$CMD_PYTHON` or `$PROJECT_ROOT`. You can set these manually or via a .env file. For example:

```bash
export CMD_PYTHON=/path/to/your/conda/envs/ny/bin/python
export PROJECT_ROOT=/path/to/this/repo
```

### 3. Pull Data & Artifacts from S3 (Optional)

Data:

```bash
python dependencies/io/pull_dvc_s3.py
```

This will configure the DVC remote (public S3) and dvc pull the relevant data into `data/`.

- ML runs (artifacts, metrics, etc.):

```bash
python dependencies/io/pull_mlruns_s3.py
```

This populates the `mlruns/` folder with finalized experiments.

### 4. Check or Adjust dvc.yaml

This repo includes a pre-generated `dvc.yaml` that defines the pipeline stages. If you find references to an environment path that doesn’t match your local machine, you may need to edit the commands in `dvc.yaml` or in `configs/pipeline/`.

⸻

## Running the Pipeline (If Desired)

### 1. Force Reproduce All Stages

```bash
dvc repro --force -P
```

This will attempt to run every stage from scratch. If you see “File already tracked by Git” or path mismatch issues, adjust your environment variables or pipeline commands in `dvc.yaml`.

### 2. Run a Single Stage

```bash
dvc repro --force -s v10_lag_columns
```

This calls:

```bash
python scripts/universal_step.py \
    setup.script_base_name=lag_columns \
    transformations=lag_columns \
    data_versions.data_version_input=v10 \
    data_versions.data_version_output=v11
```

Hydra loads `configs/transformations/lag_columns.yaml`, reads `./data/v10/v10.csv`, and writes the result plus metadata to `./data/v11/`.

### 3. Check the Logs

You’ll find logs in `logs/runs/${timestamp}`, with one file per transformation or model training step.

⸻

Running ML Experiments  
- For example, to run a Random Forest hyperparameter trial with Optuna:

```bash
python scripts/universal_step.py \
    setup.script_base_name=rf_optuna_trial \
    data_versions=v13 \
    model_params=rf_optuna_trial_params
```

This logs metrics and artifacts (model pickle, feature importances) to `mlruns/`.

⸻

## Known Caveats
1. Manual Pipeline Config Adjustments
  You may need to tweak commands in dvc.yaml or Hydra configs if your environment paths differ from mine.
  Some references to cmd_python or project root might be out of date if you cloned the repo to a different location.

2. Mixed Git/DVC Tracking
  The pipeline definition (dvc.yaml) is tracked in Git.
  Large data and model outputs are tracked by DVC. If you encounter an error about “file tracked by Git” or “tracked by both Git and DVC,” remove or untrack it from DVC.

3. S3 Accessibility
  The data and MLflow artifacts are stored in a public S3 bucket. If you can’t access them, you might need to set up AWS credentials or bypass corporate firewalls.

4. Focus on Portfolio
  This project demonstrates MLOps patterns, but it may not be fully turnkey for every environment. (For instance, the pipeline might reference paths/base.yaml with absolute paths that differ from your machine.)

⸻

## Why This Setup?

1. Config-Driven
  Hydra reduces code duplication by separating parameters (like CSV paths or hyperparams) from business logic.
2. Version Controlled & Reproducible
  DVC manages big data artifacts so that you can revert or reproduce results with minimal overhead.
3. Modular & Extensible
  Each transformation is a self-contained function plus a small YAML config. You can easily add or remove steps without rewriting the entire pipeline.
4. Experiment Management with MLflow
  MLflow logs metrics, confusion matrices, and picks up model artifacts. This helps in comparing trials and working in a team.
5. Demonstration of Best Practices
    - Logging: auto-generated metadata for CSV transformations.
    - Potential CI/CD hooks (e.g., dvc repro in a CI pipeline).
    - Clear project structure for large or enterprise MLOps setups.

⸻

## Contact
- Author: Tobias Klein
- Contact:
    - Open an issue on GitHub or message me on LinkedIn for questions.
    - [LinkedIn](https://www.linkedin.com/in/deep-learning-mastery/)
    - [Website](https://deep-learning-mastery.com/)

Thank you for exploring this project! For more information on scaling or productionizing an MLOps pipeline, reach out via GitHub issues or LinkedIn.

⸻

© 2025 Tobias Klein. All rights reserved.
This repository is provided for demonstration and personal review. No license is granted for commercial or non-commercial use, copying, modification, or distribution without explicit, written permission.
