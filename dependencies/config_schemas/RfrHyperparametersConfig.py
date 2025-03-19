# dependencies/config_schemas/RfrHyperparametersConfig.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class RfrHyperparametersConfig:
    n_estimators: Optional[dict] = None
    max_depth: Optional[dict] = None
    min_samples_split: Optional[dict] = None
    max_features: Optional[dict] = None

    min_samples_leaf: Optional[dict] = None
    min_weight_fraction_leaf: Optional[dict] = None
    max_leaf_nodes: Optional[dict] = None
    min_impurity_decrease: Optional[dict] = None
    bootstrap: Optional[dict] = None
    oob_score: Optional[dict] = None
    warm_start: Optional[dict] = None
    ccp_alpha: Optional[dict] = None
    max_samples: Optional[dict] = None
    monotonic_cst: Optional[dict] = None
