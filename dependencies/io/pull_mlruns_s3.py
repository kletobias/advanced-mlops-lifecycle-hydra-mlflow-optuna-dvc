import logging
import os
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PullMlrunsS3Config:
    bucket_name: str
    prefix: str
    local_mlruns_dir: str
    remote_uri: str
    sync_command: list[str]
    overwrite_local: bool


def pull_mlruns_s3(
    local_mlruns_dir: str,
    remote_uri: str,
    sync_command: list[str],
    overwrite_local: bool,
):
    if os.path.exists(local_mlruns_dir):
        logger.info(
            "Local mlruns directory '%s' already exists. "
            "Files pulled from S3 may overwrite local files.",
            local_mlruns_dir,
        )
        if overwrite_local:
            confirm = input("Proceed with overwriting local files? [y/N]: ")
            if confirm.lower() not in ("y", "yes"):
                logger.info("Aborted by user.")
                return
        else:
            logger.info("overwrite_local is False, aborting pull.")
            return
    else:
        os.makedirs(local_mlruns_dir, exist_ok=True)
        logger.info("Created local mlruns directory '%s'", local_mlruns_dir)

    logger.info("Pulling mlruns from '%s' to '%s'", remote_uri, local_mlruns_dir)
    subprocess.run(sync_command, check=True)
    logger.info("Pull complete.")


if __name__ == "__main__":
    import sys

    import hydra

    from dependencies.config_schemas.RootConfig import RootConfig

    sys.argv = [
        sys.argv[0],
        "utility_functions=pull_mlruns_s3",
        "remote_storage=s3_mlflow",
    ]

    @hydra.main(version_base=None, config_path="../../configs", config_name="config")
    def main(cfg: RootConfig):
        pull_mlruns_s3(
            cfg.utility_functions.local_mlruns_dir,
            cfg.utility_functions.remote_uri,
            list(cfg.utility_functions.sync_command),
            cfg.utility_functions.overwrite_local,
        )

    main()
