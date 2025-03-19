import logging

logger = logging.getLogger(__name__)
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def plot_boxenplot(
    df: pd.DataFrame,
    output_dir: str,
    figsize: tuple = (8, 4),
    title_fmt: str | None = None,
    ylabel_override: str | None = None,
    percentile_limit: float = 0.99,
) -> None:
    for col in df.select_dtypes(include=["number", "object", "category"]):
        plt.figure(figsize=figsize)
        ax = plt.gca()
        if df[col].dtype.kind in "biufc":
            data = df[col].dropna()
            if df[col].nunique() > 50:
                lower_percentile = (1 - percentile_limit) / 2 * 100
                upper_percentile = 100 - lower_percentile
                lower, upper = np.percentile(data, [lower_percentile, upper_percentile])
                truncated_lower = (data < lower).sum()
                truncated_upper = (data > upper).sum()
                total_truncated = truncated_lower + truncated_upper
                sns.boxenplot(x=data, ax=ax)
                plt.xlim(lower, upper)
                info = f"Limit: {lower_percentile:.1f}-{upper_percentile:.1f}th | Truncated: {total_truncated}"
                plt.text(
                    0.5,
                    0.95,
                    info,
                    transform=ax.transAxes,
                    ha="center",
                    va="top",
                    fontsize="small",
                    bbox={"facecolor": "white", "alpha": 0.5, "edgecolor": "none"},
                )
                plt.xlabel(col)
                if title_fmt:
                    plt.title(title_fmt.format(col=col))
                else:
                    plt.title(f"Boxenplot of {col}")
            else:
                sns.histplot(data, kde=True, ax=ax)
                plt.xlabel(col)
                if title_fmt:
                    plt.title(title_fmt.format(col=col))
                else:
                    plt.title(f"Histogram of {col}")
        else:
            sns.countplot(x=df[col].dropna(), order=df[col].value_counts().index, ax=ax)
            plt.xlabel(col)
            if title_fmt:
                plt.title(title_fmt.format(col=col))
            else:
                plt.title(f"Countplot of {col}")
        plt.ylabel(ylabel_override if ylabel_override is not None else "Frequency")
        sns.despine(top=True, right=True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{col}_distribution.png"))
        plt.close()
