import logging
import os

logger = logging.getLogger(__name__)


def mkdir_if_not_exists(directory: str) -> None:
    if not os.path.isdir(directory):
        os.makedirs(directory)
        logger.info("Created new directory: %s", directory)
    else:
        logger.info("Directory exists, skipping creation\n%s", directory)
