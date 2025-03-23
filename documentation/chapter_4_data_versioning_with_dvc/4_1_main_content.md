## 4. Data Versioning with DVC

You have `.yaml.dvc` files to store dataset version references. Each transformation script references the config path for the input data. This way:
- You can run `dvc repro v10_create_lag_features.dvc` to rebuild an older version if needed.
- Merges seamlessly with your Hydra approach, so you only update the `data_versions` config for changes.

Emphasize your process:
1. Acquire data or produce it from a preceding script.  
2. Commit data to DVC, record it in the config.  
3. The new `.yaml` under `data_versions/` describes that new data version.  
4. All subsequent scripts reference the data version name, making the pipeline fully reproducible.
