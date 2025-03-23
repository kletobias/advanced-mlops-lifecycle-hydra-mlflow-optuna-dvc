<!--documentation/chapter_3_how_runtime_overrides_work/3_1_main_content.md-->
## 3. How Runtime Overrides Work

Using Hydra, you can do:

```sh
python src/modeling/v13_rf_optuna_trial_2.py \
  setup.script_base_name=rf_optuna_trial_2 \
  data_versions=v13 \
  project_sections=5_modeling \
  ml_experiments=time_series \
  ml_experiments.mlflow.experiment_id=rf_optuna_trial_2 \
  ml_experiments.kwargs_optuna_study.n_trials=50
```
At runtime, we override some entries in the defaults list in `config.yaml`:

Instead of using the default `ml_experiments: base` we do a partial overwrite and add new key value pairs from the time series specific `time_series.yaml` config.

Mlflow will use `rf_optuna_trial_2` for setting the experiment_id, and we increase the value for `n_trials` that optuna uses to 50.

- **Critical Thinking**: You mention you “try not to duplicate” things—Hydra supports exactly that by letting you define a “base” config, then override only what changes.  
- **Example**: You can jump from `v1` to `v10` data version just by specifying `+data_versions=v10`; no rewriting of paths in your code is necessary.
