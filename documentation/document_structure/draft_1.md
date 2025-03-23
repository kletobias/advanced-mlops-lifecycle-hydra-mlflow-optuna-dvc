<!--documentation/document_structure/draft_1.md-->

Below is a suggested outline and approach for creating thorough, readable documentation that highlights your design decisions, critical thinking, and senior-level DevOps/ML engineering practices. You could publish this as one or more articles/posts, or a dedicated “Technical Design” section on your portfolio website and LinkedIn.

---

## 1. High-Level Overview

### 1.1 Objectives and Motivations

- **Why** you built the project the way you did (e.g., reproducibility, clarity for future contributors, runtime flexibility, data versioning).  
- **What** the project accomplishes: a complete ML pipeline from ingestion to evaluation, with an emphasis on maintainability and DevOps best practices.

### 1.2 Architecture at a Glance

- **Config Management**: Hydra + Omegaconf for hierarchical config groups.  
- **Versioning**: DVC for dataset tracking; Git for code.  
- **Pipelines**: A sequence of transformations, each with its own script, all orchestrated by Hydra overrides.  
- **Documentation**: All separated into clear config groups so each piece of the pipeline can be easily understood and overridden.

A simple diagram or bullet list helps here:

```
┌───────────────────────┐
│ Ingestion & Cleaning  │  <-- Hydra “project_sections” group
└───────────────────────┘
          ↓
┌───────────────────────┐
│  Transformation       │  <-- Hydra “transformation” group
└───────────────────────┘
          ↓
┌───────────────────────┐
│  Partitioning & Model │  <-- Hydra “partitioning” and “models” groups
└───────────────────────┘
          ↓
┌───────────────────────┐
│  Evaluation & Logging │  <-- Hydra “evaluation” and “logging” groups
└───────────────────────┘
```

---

## 2. Config Groups and Rationale

### 2.1 Overall Structure

Explain your “configs/” folder layout and **why** it’s split into multiple subfolders. Emphasize:
- **Separation of Concerns**: Each group focuses on a specific domain (e.g. `data_versions/`, `models/`, `setup/`).
- **Reduced Duplication**: You override only the parts that need changing for each run or environment, instead of copying entire config files.
- **Future-Proofing**: As the project grows (new data versions, new modeling techniques), you simply add or override configs.

### 2.2 Notable Folders

- **configs/data_versions**  
  Tracks each new “version” of data—each `.yaml` in here points to the CSV/DB file path, includes a short description, and references the parent `base.yaml`. This ensures you can reproduce or revert to any historical data transformation via DVC.  
  - **Critical Thinking**: You documented the transformations in `description:` fields for each version, so someone can read them and see exactly what changed.

- **configs/models**  
  Contains `base.yaml`, `randomforest.yaml`, `catboost.yaml`, etc. You only need to change one line (e.g. `- models: catboost`) to pick a different model.  
  - **Critical Thinking**: This avoids “copy-paste” duplication. You keep your code the same but can switch model configs at runtime.

- **configs/ml_experiments**  
  Contains cross-validation parameters, MLflow experiment directories, etc. You can unify the tracking logic for every training run here, so you don’t bury hyperparameters inside code.

- **configs/logging**, **configs/hydra**  
  Central location for logging level, Hydra job output directories, job naming conventions, etc.  
  - **Critical Thinking**: Centralized logging ensures consistent logging format across every script and an easy place to tweak log levels.

- **configs/project_sections**  
  Maps to each pipeline stage: ingestion (`0_ingestion.yaml`), transformation (`3_transformation.yaml`), and so forth. You can see how each step is configured and chained, which is important for a typical “data-lifecycle” approach.

- **configs/setup**  
  Contains base settings for templated Python scripts. Also references your Jinja-based approach to automatically generate or update scripts.

- **configs/templates**  
  Jinja2 templates that define default structure for new scripts or configs, so you can spin up consistent transformations quickly without rewriting boilerplate.

---

## 3. How Runtime Overrides Work

Using Hydra, you can do:

```
python src/transformation/v10_create_lag_features.py +models=catboost +data_versions=v10
```

to override the default `models: randomforest` and `data_versions: base` in `config.yaml`. This makes the same script reusable for different scenarios, because you separate your logic from the parameters.

- **Critical Thinking**: You mention you “try not to duplicate” things—Hydra supports exactly that by letting you define a “base” config, then override only what changes.  
- **Example**: You can jump from `v1` to `v10` data version just by specifying `+data_versions=v10`; no rewriting of paths in your code is necessary.

---

## 4. Data Versioning with DVC

You have `.yaml.dvc` files to store dataset version references. Each transformation script references the config path for the input data. This way:
- You can run `dvc repro v10_create_lag_features.dvc` to rebuild an older version if needed.
- Merges seamlessly with your Hydra approach, so you only update the `data_versions` config for changes.

Emphasize your process:
1. Acquire data or produce it from a preceding script.  
2. Commit data to DVC, record it in the config.  
3. The new `.yaml` under `data_versions/` describes that new data version.  
4. All subsequent scripts reference the data version name, making the pipeline fully reproducible.

---

## 5. Modular Code Organization

### 5.1 “Dependencies” Folder

This is where you store reusable logic:
- **cleaning**: e.g. `sanitize_column_names.py`
- **io**: read/write CSV or JSON logic
- **metadata**: computing metadata, hashing, etc.
- **modeling**: training logic, logging model importances, etc.

Highlight how each submodule is small and focused, letting you:
- Keep the pipeline scripts lean.
- Avoid rewriting file I/O or logging code repeatedly.
- Achieve easier testing and maintenance.

### 5.2 “src/” Folder

Contains the actual pipeline steps (one script per data transformation version). Each script typically:
1. Reads config values (paths, columns, etc.).
2. Reads in data from a CSV or DB.
3. Applies the transformation logic.
4. Saves the new data version + logs metadata.

---

## 6. Example Walkthrough: A Data Transformation Step

Pick a single transformation script (e.g., `src/transformation/v10_create_lag_features.py`) and:
1. **Show the relevant config** (the default in `configs/data_versions/v10.yaml`).  
2. **Show the Hydra override** you might run, e.g. `python v10_create_lag_features.py data_versions=v10`.  
3. **Show the final data artifacts** (the output CSV, a new DVC file, updated metadata JSON).  
4. **Explain the “why”** behind adding lag features, how you group by facility and shift by year, and how you decided which columns to shift.

This ties everything together: from config definitions → script logic → resulting data version → logging → DVC.

---

## 7. Logging and MLflow Integration

- **Centralized Logging**: “configs/logging/default.yaml” sets the format and level. Show how each step logs to a unique file so you can quickly debug transformations or model training.  
- **MLflow**: “configs/ml_experiments/base.yaml” centralizes experiment output directories, artifact paths, etc. Emphasize how all experiments get versioned + tracked with minimal code changes.

---

## 8. Conclusion and Further Steps

Finish your documentation with:
1. A short recap: how Hydra + separate config groups + DVC + modular code all work together.  
2. Potential expansions, e.g. “We could add Docker or more CI/CD for fully automated pipelines,” or “We might add pre-commit hooks to lint these configs.”

You can also embed links to any Jupyter notebooks or final dashboards that interpret results, so prospective employers can see both the engineering and the analytics side.

---

## 9. Where to Publish This Documentation

- **Portfolio Website**: Create a dedicated “Project: Medical DRG in NY” page with sections or an accordion menu for each piece. Link from your main portfolio.  
- **LinkedIn Articles**: Post shorter, more high-level or conceptual pieces. Emphasize your design thinking, how you overcame potential pitfalls, and how you integrated Hydra + DVC.  
- **GitHub Wiki or Repository README**: Provide a quick reference so recruiters or collaborators can see how to run the pipeline.

---

### Final Thoughts

Your deep config hierarchy and script structure is already a big demonstration of senior-level MLOps thinking. By writing the documentation with clear “why” explanations, you show your ability to design maintainable systems, keep data transformations reproducible, and integrate best practices (DVC, Hydra, MLflow). That’s exactly what hiring managers for senior ML/DevOps roles are looking for.
