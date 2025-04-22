# dependencies/io/push_mlruns_s3.py
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PushMlrunsS3Config:
    bucket_name: str
    prefix: str
    local_mlruns_dir: str
    remote_uri: str
    sync_command: Any
    replace_remote: bool


def push_mlruns_s3(
    local_mlruns_dir: str,
    remote_uri: str,
    sync_command: Any,
    replace_remote: bool,
):
    if not os.path.exists(local_mlruns_dir):
        logger.error(
            "Aborting push: Local mlruns directory %s does not exist",
            local_mlruns_dir,
        )
        return

    if replace_remote:
        logger.info("Remote objects not present locally will be deleted from S3.")
        confirm = input("Proceed with remote deletion? [y/N]: ")
        if confirm.lower() not in ("y", "yes"):
            logger.info("Aborted by user.")
            return
        sync_command += ["--delete"]

    logger.info(
        "Syncing local mlruns from '%s' to '%s' (including '.trash/' and hidden files)",
        local_mlruns_dir,
        remote_uri,
    )
    subprocess.run(sync_command, check=True)
    logger.info("Push complete.")


if __name__ == "__main__":
    import sys

    import hydra

    from dependencies.config_schemas.RootConfig import RootConfig

    sys.argv = [
        sys.argv[0],
        "utility_functions=push_mlruns_s3",
        "remote_storage=s3_mlflow",
    ]

    @hydra.main(version_base=None, config_path="../../configs", config_name="config")
    def main(cfg: RootConfig):
        push_mlruns_s3(
            cfg.utility_functions.local_mlruns_dir,
            cfg.utility_functions.remote_uri,
            cfg.utility_functions.sync_command,
            cfg.utility_functions.replace_remote,
        )

    main()
