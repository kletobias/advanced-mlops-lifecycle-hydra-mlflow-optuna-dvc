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
