# dependencies/config_schemas/RidgeHyperparametersConfig.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class RidgeHyperparametersConfig:
    alpha: Optional[dict] = None
    solver: Optional[dict] = None
    tol: Optional[dict] = None
    max_iter: Optional[dict] = None
