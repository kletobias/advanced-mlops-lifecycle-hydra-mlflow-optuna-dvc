import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd

from config_schemas.RootConfig import RootConfig
from dependencies.general.make_relative_file_path import anonymize_path
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.metadata.compute_file_hash import compute_file_hash

logger = logging.getLogger(__name__)


def compute_dataframe_hash(df: pd.DataFrame) -> str:
    df_string = df.to_csv(index=True)
    return hashlib.sha256(df_string.encode("utf-8")).hexdigest()


def get_column_metadata(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    metadata = {}
    for col in df.columns:
        metadata[col] = {
            "data_type": str(df[col].dtype),
            "num_missing": int(df[col].isnull().sum()),
            "unique_values": int(df[col].nunique()),
            "memory_usage_bytes": int(df[col].memory_usage(deep=True)),
        }
    return metadata


def get_index_metadata(df: pd.DataFrame) -> dict[str, Any]:
    index_info = {
        "index_type": type(df.index).__name__,
        "name": df.index.name,
    }
    if isinstance(df.index, pd.RangeIndex):
        index_info.update(
            {"start": df.index.start, "stop": df.index.stop, "step": df.index.step},
        )
    elif isinstance(df.index, pd.DatetimeIndex):
        start_ts = df.index.min()
        end_ts = df.index.max()
        # Safely convert any valid Timestamps to ISO strings
        start_iso = start_ts.isoformat() if not pd.isnull(start_ts) else None
        end_iso = end_ts.isoformat() if not pd.isnull(end_ts) else None
        index_info.update(
            {
                "start": start_iso,
                "end": end_iso,
                "frequency": df.index.freqstr if df.index.freqstr else None,
            },
        )
    elif isinstance(df.index, pd.MultiIndex):
        index_info.update({"levels": df.index.nlevels, "names": list(df.index.names)})
    return index_info


def calculate_metadata(df: pd.DataFrame, data_file_path: str) -> dict[str, Any]:
    timestamp = datetime.utcnow().isoformat() + "Z"
    try:
        file_size = os.path.getsize(data_file_path)
    except OSError:
        file_size = None
        logger.warning("File size could not be determined for %s.", data_file_path)

    num_rows = len(df)
    df_hash = compute_dataframe_hash(df)

    try:
        hash_sha256 = compute_file_hash(data_file_path)
    except Exception as e:
        logger.error("Error computing file hash for %s: %s", data_file_path, e)
        hash_sha256 = None

    updated_file_path = anonymize_path(data_file_path)
    columns_metadata = get_column_metadata(df)
    index_metadata = get_index_metadata(df)

    metadata = {
        "timestamp": timestamp,
        "file_path": updated_file_path,
        "file_size_bytes": file_size,
        "num_rows": num_rows,
        "hash_sha256": hash_sha256,
        "df_hash": df_hash,
        "total_columns": df.shape[1],
        "columns": columns_metadata,
        "index": index_metadata,
    }

    logger.info("Generated metadata for file: %s", data_file_path)
    logger.debug("Metadata details: %s", json.dumps(metadata, indent=4))
    return metadata


def save_metadata(metadata: dict[str, Any], metadata_file: str):
    try:
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)
        logger.info("Metadata successfully saved to %s", metadata_file)
    except Exception as e:
        logger.error("Error saving metadata to %s: %s", metadata_file, e)


def load_metadata(metadata_file: str) -> dict[str, Any]:
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
        logger.info("Metadata successfully loaded from %s", metadata_file)
        return metadata
    except Exception as e:
        logger.error("Error loading metadata from %s: %s", metadata_file, e)
        return {}


def validate_data_file_path(data_file_path: str) -> None:
    assert os.path.exists(data_file_path), "Data file does not exist"


@log_function_call
def calculate_and_save_metadata(
    df: pd.DataFrame,
    data_file_path: str,
    output_metadata_file_path: str,
) -> None:
    validate_data_file_path(data_file_path)
    metadata = calculate_metadata(df, data_file_path)
    save_metadata(metadata, output_metadata_file_path)
