# dependencies/io/pull_dvc_s3.py
import logging
import subprocess
import sys
from dataclasses import dataclass

import hydra

from dependencies.config_schemas.RootConfig import RootConfig

logger = logging.getLogger(__name__)


@dataclass
class DvcPullS3Config:
    """Holds the config needed to pull from a DVC remote on S3."""

    remote_uri: str
    remote_name: str


def pull_dvc_s3(
    remote_uri: str,
    remote_name: str,
    num_parts_expected: int = 2,
) -> None:
    """1) Checks if 'remote_name' is in DVC's remote list.
    2) If not, adds it via: dvc remote add -d <remote_name> <remote_uri>.
    3) Finally calls: dvc pull -r <remote_name>.
    """
    try:
        out = subprocess.check_output(["dvc", "remote", "list"], text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to list DVC remotes: %s", e)

    # Parse existing remote lines into a dict
    existing_remotes = {}
    for line in out.strip().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == num_parts_expected:
            existing_remotes[parts[0]] = parts[1]

    if remote_name in existing_remotes:
        logger.info(
            "DVC remote '%s' already exists: %s",
            remote_name,
            existing_remotes[remote_name],
        )
    else:
        logger.info("Adding DVC remote '%s' -> %s", remote_name, remote_uri)
        try:
            subprocess.run(
                ["dvc", "remote", "add", "-d", remote_name, remote_uri],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error("Failed to add DVC remote: %s", e)

    logger.info("Pulling data from remote '%s'", remote_name)
    try:
        subprocess.run(["dvc", "pull", "-r", remote_name], check=True)
        logger.info("DVC pull complete.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to pull DVC data: %s", e)


if __name__ == "__main__":
    sys.argv = [sys.argv[0], "utility_functions=pull_dvc_s3", "remote_storage=s3_dvc"]

    @hydra.main(version_base=None, config_path="../../configs", config_name="config")
    def main(cfg: RootConfig) -> None:
        """Expects something like:

        remote_storage:
          s3_bucket:
            remote_uri: "s3://nyproject25/dvc"

        utility_functions:
          remote_uri: ${remote_storage.s3_bucket.remote_uri}
          remote_name: "s3_dvc"
        """
        dvc_cfg = DvcPullS3Config(
            remote_uri=cfg.utility_functions.remote_uri,
            remote_name=cfg.utility_functions.remote_name,
        )
        pull_dvc_s3(**dvc_cfg.__dict__)

    main()
