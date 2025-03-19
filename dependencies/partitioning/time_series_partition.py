import pandas as pd
from sklearn.model_selection import TimeSeriesSplit


def time_series_partition(
    df: pd.DataFrame,
    feature_cols: list[str],
    year_col: str,
    train_range: tuple[int, int],
    val_range: tuple[int, int],
    test_range: tuple[int, int],
    target_col: str,
) -> dict[str, pd.DataFrame]:
    """Slices a DataFrame by year into train, val, and test sets,
    returning a dictionary with X/y for each slice.
    """
    df_train = df[
        (df[year_col] >= train_range[0]) & (df[year_col] <= train_range[1])
    ]  # changed
    df_val = df[
        (df[year_col] >= val_range[0]) & (df[year_col] <= val_range[1])
    ]  # changed
    df_test = df[
        (df[year_col] >= test_range[0]) & (df[year_col] <= test_range[1])
    ]  # changed

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_val, y_val = df_val[feature_cols], df_val[target_col]
    X_test, y_test = df_test[feature_cols], df_test[target_col]

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
    }


def create_time_series_cv(n_splits: int = 4) -> TimeSeriesSplit:
    """Returns a TimeSeriesSplit object for chronological cross-validation."""
    return TimeSeriesSplit(n_splits=n_splits)
