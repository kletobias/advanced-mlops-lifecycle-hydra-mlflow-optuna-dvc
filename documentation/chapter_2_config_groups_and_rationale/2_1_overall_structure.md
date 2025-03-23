## 2. Config Groups and Rationale

### 2.1 Overall Structure

#### Reasoning Behind the Config Group Structure

I organized my config groups so each remains **narrowly scoped** and **optional**, rather than lumping everything into a single, monolithic configuration. For instance, MLflow settings and ML experiment parameters live in their own group, so they only get composed when relevant. This enforces **Separation of Concerns**: if a script doesn’t need ML experiments, it doesn’t import extra settings, staying clean and minimal.

I also create a **base** config for each group—covering shared, **default** keys—and then **override** only the parts that change for specific runs or features. That significantly **Reduces Duplication** and clarifies each group’s role. Consistent naming conventions (`*_file_path`, `*_directory_path`, etc.) map directly to Python variable names, ensuring **traceability** of where each parameter originates.

Furthermore, I define all paths as **absolute** within the config, often using OmegaConf interpolation (e.g., `${paths.directories.data}/${data_versions.data_version}.csv`). That way, I can reference directory keys and filenames without resorting to ad-hoc `os.path.join` calls in code—again enhancing **Separation of Concerns**. The Python scripts simply consume final, resolved paths, and the config orchestrates how those paths are constructed.

This approach leads to **Future-Proofing**: as requirements evolve (e.g., new data sources or model pipelines), I can introduce or override configs without refactoring existing scripts. Each piece stays **modular**, **maintainable**, and **reproducible**, aligning with senior-level MLOps best practices. 
