"""Plot of ECDF."""

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")
logger = logging.getLogger(__name__)


def plot_cdf(
    df: pd.DataFrame,
    output_dir: str,
    figsize: tuple = (8, 4),
    title_fmt: str | None = None,
    ylabel_override: str | None = None,
) -> None:
    """ECDF Plot."""
    for col in df.select_dtypes(include=["number"]):
        s = pd.DataFrame(df[col].dropna())
        if s.empty:
            continue
        plt.figure(figsize=figsize)
        sns.kdeplot(data=s, cumulative=True)
        plt.xlabel(col)
        if title_fmt:
            plt.title(title_fmt.format(col=col))
        else:
            plt.title(f"CDF of {col}")
        if ylabel_override is not None:
            plt.ylabel(ylabel_override)
        else:
            plt.ylabel("Cumulative Density")
        sns.despine(top=True, right=True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{col}_cdf.png"))
        plt.close()
