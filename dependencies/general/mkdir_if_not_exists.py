import logging

logger = logging.getLogger(__name__)
import os


def mkdir_(directory: str) -> None:
    if not os.path.isdir(directory):
        os.makedirs(directory)
        logger.info("Created new directory: %s", directory)
    else:
        logger.info("Directory exists, skipping creation\n%s", directory)
