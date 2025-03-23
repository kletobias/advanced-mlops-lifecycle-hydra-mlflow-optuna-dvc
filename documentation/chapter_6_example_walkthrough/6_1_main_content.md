## 6. Example Walkthrough: A Data Transformation Step

Pick a single transformation script (e.g., `src/transformation/v10_create_lag_features.py`) and:
1. **Show the relevant config** (the default in `configs/data_versions/v10.yaml`).
2. **Show the Hydra override** you might run, e.g. `python v10_create_lag_features.py data_versions=v10`.
3. **Show the final data artifacts** (the output CSV, a new DVC file, updated metadata JSON).
4. **Explain the “why”** behind adding lag features, how you group by facility and shift by year, and how you decided which columns to shift.

This ties everything together: from config definitions → script logic → resulting data version → logging → DVC.
