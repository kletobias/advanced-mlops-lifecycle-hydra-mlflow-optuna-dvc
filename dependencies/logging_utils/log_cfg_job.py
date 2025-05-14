# dependencies/logging_utils/log_cfg_job.py
import logging

from omegaconf import OmegaConf

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.general.mkdir_if_not_exists import mkdir_if_not_exists

logger = logging.getLogger(__name__)


def log_cfg_job(cfg: RootConfig) -> None:
    output_cfg_job_file_path = cfg.logging_utils.log_cfg_job.output_cfg_job_file_path
    output_cfg_job_directory_path = (
        cfg.logging_utils.log_cfg_job.output_cfg_job_directory_path
    )
    resolve = cfg.logging_utils.log_cfg_job.resolve
    logger.debug(
        "output_file_path for `cfg --job` export is %s",
        output_cfg_job_file_path,
    )
    # Create parent directory, if it doesn't exist
    mkdir_if_not_exists(output_cfg_job_directory_path)
    try:
        OmegaConf.save(cfg, output_cfg_job_file_path, resolve=resolve)
        if resolve:
            logger.debug("Successfully saved '--cfg job --resolve' output to file")
        else:
            logger.debug("Successfully saved '--cfg job' output to file")
    except Exception as e:
        logger.error("Error resolving or saving the config: %s", e)  # changed
        raise
