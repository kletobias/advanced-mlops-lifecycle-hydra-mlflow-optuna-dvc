# dependencies/modeling/optuna_random_search_util.py
import logging

import optuna

logger = logging.getLogger(__name__)


def optuna_random_search_util(
    trial: optuna.Trial,
    hyperparameters: dict,
) -> dict:
    """1) Start with DEFAULT_RF_PARAMS as baseline.
    2) For each param in param_config:
       - If tune==true, call trial.suggest_* and override baseline.
       - If tune==false and we have fixed_value, override baseline with that.
       - Else keep the default from DEFAULT_RF_PARAMS.
    3) Returns a final dict ready for RandomForestRegressor(**final_params).
    """
    final_params = {}
    for param_name, param_values in hyperparameters.items():
        tune_flag = param_values.get("tune", False)
        p_type = param_values.get("type", None)
        step = param_values.get("step", None)
        log = param_values.get("log", None)

        if tune_flag:
            if p_type == "int":
                low = param_values["low"]
                high = param_values["high"]
                if step:
                    final_params[param_name] = trial.suggest_int(
                        param_name,
                        low,
                        high,
                        step,
                    )
                else:
                    final_params[param_name] = trial.suggest_int(param_name, low, high)
            elif p_type == "float":
                low = param_values["low"]
                high = param_values["high"]
                if step:
                    if log:
                        final_params[param_name] = trial.suggest_float(
                            param_name,
                            low,
                            high,
                            step,
                            log=True,
                        )
                    else:
                        final_params[param_name] = trial.suggest_float(
                            param_name,
                            low,
                            high,
                            step,
                        )
                else:
                    if log:
                        final_params[param_name] = trial.suggest_float(
                            param_name,
                            low,
                            high,
                            log=True,
                        )
                    else:
                        final_params[param_name] = trial.suggest_float(
                            param_name,
                            low,
                            high,
                        )
            elif p_type == "bool":
                final_params[param_name] = trial.suggest_categorical(
                    param_name,
                    [True, False],
                )
            elif p_type == "categorical":
                values = list(param_values["values"])
                final_params[param_name] = trial.suggest_categorical(param_name, values)
            else:
                msg = f"Unsupported param type '{p_type}' for tuning."
                raise ValueError(msg)
        else:
            logger.debug(
                "Parameter %s not included in hyperparameter search. Tune: %s",
                param_name,
                tune_flag,
            )

    return final_params
