import logging
import subprocess
from dataclasses import dataclass
from typing import NoReturn

logger = logging.getLogger(__name__)

@dataclass
class DvcPushS3Config:
    """
    Holds the config needed to push to a DVC remote on S3.
    """
    remote_uri: str
    remote_name: str

def push_dvc_s3(remote_uri: str, remote_name: str) -> NoReturn:
    """
    1) Checks if 'remote_name' is in DVC's remote list.
    2) If not, adds it via: dvc remote add -d <remote_name> <remote_uri>.
    3) Finally calls: dvc push -r <remote_name>.
    """
    try:
        out = subprocess.check_output(["dvc", "remote", "list"], text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to list DVC remotes: %s", e)
        return

    # Parse existing remote lines into a dict
    existing_remotes = {}
    for line in out.strip().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            existing_remotes[parts[0]] = parts[1]

    if remote_name in existing_remotes:
        logger.info("DVC remote '%s' already exists: %s", remote_name, existing_remotes[remote_name])
    else:
        logger.info("Adding DVC remote '%s' -> %s", remote_name, remote_uri)
        try:
            subprocess.run(["dvc", "remote", "add", "-d", remote_name, remote_uri], check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to add DVC remote: %s", e)
            return

    logger.info("Pushing data to remote '%s'", remote_name)
    try:
        subprocess.run(["dvc", "push", "-r", remote_name], check=True)
        logger.info("DVC push complete.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to push DVC data: %s", e)

if __name__ == "__main__":
    import hydra
    from dependencies.config_schemas.RootConfig import RootConfig
    import sys
    sys.argv = [
        sys.argv[0], # Number of overrides: 2
        'utility_functions=push_dvc_s3',
        'remote_storage=s3_dvc'
    ]

    @hydra.main(version_base=None, config_path="../../configs", config_name="config")
    def main(cfg: RootConfig) -> None:
        """
        Expects something like:
        
        remote_storage:
          s3_bucket:
            remote_uri: "s3://nyproject25/dvc"

        utility_functions:
          dvc_s3_push:
            remote_uri: ${remote_storage.s3_bucket.remote_uri}
            remote_name: "myremote"
        """
        # Create dataclass instance from Hydra config
        dvc_cfg = DvcPushS3Config(
            remote_uri=cfg.utility_functions.remote_uri,
            remote_name=cfg.utility_functions.remote_name,
        )
        # Call the function with explicit args
        push_dvc_s3(**dvc_cfg.__dict__)

    main()
