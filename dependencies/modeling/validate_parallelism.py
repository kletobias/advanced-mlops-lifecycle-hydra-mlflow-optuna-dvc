# dependencies/modeling/validate_parallelism.py
import logging
import multiprocessing

from dependencies.config_schemas.RootConfig import RootConfig

logger = logging.getLogger(__name__)

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def detect_max_cores(use_physical: bool = False) -> int:
    """
    Returns the number of CPU cores on this machine.
    If use_physical=True and psutil is installed, returns physical core count.
    Otherwise returns the total logical cores (incl. hyperthreads).
    """
    if use_physical and HAS_PSUTIL:
        cores = psutil.cpu_count(logical=False)
        if cores is not None:
            return cores
        # If psutil returns None, fallback to logical count below

    # Fallback to logical count (built-in or psutil logical)
    return multiprocessing.cpu_count()


def validate_jobs(n_jobs_cv: int, n_jobs_study: int, max_cores: int = None) -> None:
    """
    Checks if the total parallel usage for cross_validate (n_jobs_cv)
    and parallel Optuna trials (n_jobs_study) exceed the available cores.
    If n_jobs=-1, we interpret it as 'use all' (== max_cores).
    Raises ValueError if the product goes beyond the detected core count.
    """
    if max_cores is None:
        max_cores = detect_max_cores(use_physical=False)  # or True for physical cores

    # Convert -1 => max_cores
    n_cv = max_cores if n_jobs_cv == -1 else n_jobs_cv
    n_study = max_cores if n_jobs_study == -1 else n_jobs_study

    total_cores_assigned = n_cv * n_study
    if total_cores_assigned > max_cores:
        raise ValueError(
            f"You requested {n_cv} cores for cross_validate and {n_study} parallel trials, "
            f"total {n_cv * n_study}, which exceeds available {max_cores}."
        )

    logger.debug(
        "Exiting function 'validate_jobs' successfully with requested cores: %i ",
        total_cores_assigned,
    )


def validate_parallelism(n_jobs_cv: int, n_jobs_study: int) -> None:
    max_cores = detect_max_cores(use_physical=False)
    validate_jobs(n_jobs_cv, n_jobs_study, max_cores)
