# dependencies/modeling/remove_stale_mlflow_dirs.py
import logging
import os
import shutil
import time

logger = logging.getLogger(__name__)


def remove_stale_mlflow_dirs(mlflow_root: str):
    now = time.time()
    max_age_seconds = 60 * 60  # e.g. 1 hour
    for name in os.listdir(mlflow_root):
        if name in ("models", ".trash"):
            continue
        maybe_exp_dir = os.path.join(mlflow_root, name)
        if os.path.isdir(maybe_exp_dir):
            mtime = os.path.getmtime(maybe_exp_dir)
            if now - mtime > max_age_seconds:
                meta_path = os.path.join(maybe_exp_dir, "meta.yaml")
                if not os.path.exists(meta_path):
                    shutil.rmtree(maybe_exp_dir)
                    logger.info("Removed stale MLflow dir: %s", maybe_exp_dir)
