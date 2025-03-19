import logging

logger = logging.getLogger(__name__)
import hashlib


def compute_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    logger.info("Generated file hash: %s", sha256_hash.hexdigest())
    return sha256_hash.hexdigest()
