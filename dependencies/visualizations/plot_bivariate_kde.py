# dependencies/visualizations/plot_bivariate_kde.py
import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)
sns.set_theme(style="whitegrid")


def plot_bivariate_kde(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_dir: str,
    xy_lim: tuple | None = None,
    log_scale: bool = False,
    filename: str = "bivariate_kde.png",
    figsize: tuple = (10, 8),
) -> None:
    """Filters data to positive values, log-transforms, then plots a 2D KDE.
    Returns None, saves plot to disk.
    """
    # Make copy to avoid altering original data
    tmp = df[[x_col, y_col]].dropna().copy()  # changed line
    tmp = tmp[(tmp[x_col] > 0) & (tmp[y_col] > 0)]  # changed line
    if tmp.empty:  # changed line
        logger.warning("No valid data after filtering; plot not created.")
        return

    # Log transform so the density is meaningful
    if log_scale:
        tmp[x_col] = np.log10(tmp[x_col])  # changed line
        tmp[y_col] = np.log10(tmp[y_col])  # changed line

    # Create and size figure
    if xy_lim:
        g = sns.jointplot(
            data=tmp,
            x=x_col,
            y=y_col,
            kind="kde",
            marginal_ticks=True,
            xlim=xy_lim[0],
            ylim=xy_lim[1],
        )  # changed line
    else:
        g = sns.jointplot(
            data=tmp,
            x=x_col,
            y=y_col,
            kind="kde",
            marginal_ticks=True,
        )  # changed line

    g.fig.set_size_inches(figsize)  # changed line
    if log_scale:
        g.set_axis_labels(f"log10({x_col})", f"log10({y_col})")  # changed line
        g.fig.suptitle(
            f"Bivariate KDE of {x_col} vs {y_col} (log10 scale)",
            y=1.01,
        )  # changed line
    else:
        g.set_axis_labels(f"{x_col}", f"{y_col}")  # changed line
        g.fig.suptitle(f"Bivariate KDE of {x_col} vs {y_col}", y=1.01)  # changed line

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, filename)
    g.fig.savefig(save_path)
    plt.close(g.fig)
    logger.info(f"Saved bivariate KDE plot to {save_path}")
