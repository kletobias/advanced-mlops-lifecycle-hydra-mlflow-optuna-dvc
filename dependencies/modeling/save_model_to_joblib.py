import logging

logger = logging.getLogger(__name__)
import hashlib
from datetime import datetime
from pathlib import Path

import joblib
from mkdir_if_not_exists import mkdir_


def verify_valid_model_type(model_type: str, valid_model_types: list[str]) -> None:
    assert model_type in valid_model_types, (
        f"Error: {model_type} not in {valid_model_types}"
    )


def generate_model_file_name(
    model_type: str,
    timestamp: str,
    valid_model_types: list[str],
) -> str:
    verify_valid_model_type(model_type, valid_model_types)
    timestamp_hash = hashlib.md5(str(timestamp).encode()).hexdigest()[:6]
    return f"{model_type.lower()}_{timestamp}_{timestamp_hash}.joblib"


def generate_destination_file_path(
    destination_directory: str,
    model_file_name: str,
) -> str:
    """Joins directory path, and filename. Returns complete file path.

    Args:
    ----
        destination_directory (str): Set by DictConfig cfg from `models.destination_directory`

    Returns: Joined path
    """
    mkdir_(destination_directory)
    return str(Path(destination_directory) / model_file_name)


def save_model(
    model,
    model_type: str,
    valid_model_types: list[str],
    destination_directory: str,
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    model_file_name = generate_model_file_name(model_type, timestamp, valid_model_types)
    destination_file_path = generate_destination_file_path(
        destination_directory,
        model_file_name,
    )
    joblib.dump(model, destination_file_path)
    logger.info("Exported %s to %s", model_file_name, destination_file_path)
