### 1.2 Architecture at a Glance

- **Config Management**:  
  Hydra + Omegaconf for hierarchical config groups.

- **Versioning**:  
  DVC for dataset tracking and Git for code, ensuring reproducible and traceable updates.

- **Pipelines**:  
  A sequence of transformations, each with its own script, all orchestrated by Hydra overrides.  

- **Documentation**:  
  Organized into distinct config groups, making each part of the pipeline clear, reusable, and easily overridden.

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
