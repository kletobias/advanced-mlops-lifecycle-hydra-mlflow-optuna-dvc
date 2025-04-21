# scripts/orchestrate_dvc_flow.py
import logging
import os
import subprocess
from typing import Any

import hydra
from prefect import flow, get_run_logger, task

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.logging_utils.log_function_call import log_function_call
from dependencies.logging_utils.setup_logging import setup_logging
from dependencies.templates.generate_dvc_yaml_core import generate_dvc_yaml_core


@task
def set_environment_vars():
    """Sets environment variables so Hydra shows full errors (no short tracebacks),
    and OmegaConf displays root cause errors.
    """
    logger = get_run_logger()
    logger.info("Setting environment variables for Hydra/OC errors")
    os.environ["HYDRA_FULL_ERROR"] = "1"
    os.environ["OC_CAUSE"] = "1"


@task
def ensure_dvc_is_clean():
    """Checks if there are uncommitted DVC files. If so, raises RuntimeError."""
    logger = get_run_logger()
    logger.info("Checking for uncommitted DVC changes")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.decode()
    changes = [
        line
        for line in result.splitlines()
        if ("dvc.yaml" in line or line.strip().endswith(".dvc"))
    ]
    if changes:
        logger.error("Found uncommitted changes in DVC files")
        msg = "Uncommitted DVC changes. Commit or stash them first."
        raise RuntimeError(msg)
    logger.info("No uncommitted DVC changes found")


@task
def generate_dvc_yaml(
    stages_list: list,
    search_path: str,
    template_name: str,
    dvc_yaml_file_path: str,
    allow_dvc_changes: bool = False,
):
    """1) If dvc.yaml does NOT exist, run the script, done.
    2) If dvc.yaml exists, rename to dvc.yaml.tmp
    3) Generate a fresh dvc.yaml via the script
    4) If new dvc.yaml differs from dvc.yaml.tmp:
         - If allow_dvc_changes=True, accept new.
         - Otherwise revert to tmp and raise RuntimeError
       Else restore dvc.yaml.tmp as final (no changes).
    """
    logger = get_run_logger()
    logger.info("Attempting to generate dvc.yaml for diff checking")

    original_path = "dvc.yaml"
    temp_path = "dvc.yaml.tmp"
    original_exists = os.path.exists(original_path)

    if original_exists:
        logger.info("Backing up existing dvc.yaml as dvc.yaml.tmp")
        os.rename(original_path, temp_path)
    else:
        logger.info("No existing dvc.yaml found")

    generate_dvc_yaml_core(
        stages_list,
        search_path,
        template_name,
        dvc_yaml_file_path,
    )

    if not original_exists:
        logger.info("Created new dvc.yaml with no prior version to compare")
        return

    if not os.path.exists(original_path):
        logger.warning("No new dvc.yaml was created; restoring from dvc.yaml.tmp")
        os.rename(temp_path, original_path)
        return

    with open(temp_path) as f_old, open(original_path) as f_new:
        old_content = f_old.read()
        new_content = f_new.read()

    if old_content == new_content:
        logger.info("No differences detected between old and new dvc.yaml")
        os.remove(original_path)
        os.rename(temp_path, original_path)
    elif not allow_dvc_changes:
        logger.error(
            "New dvc.yaml differs from existing and allow_dvc_changes=False",
        )
        os.remove(original_path)
        os.rename(temp_path, original_path)
        msg = "New dvc.yaml differs. Use allow_dvc_changes=True to overwrite."
        raise RuntimeError(
            msg,
        )
    else:
        logger.info("Accepting new dvc.yaml because allow_dvc_changes=True")
        os.remove(temp_path)


@task
def run_dvc_repro(
    stages: list[str] | None = None,
    force: bool = False,
    pipeline: bool = False,
    log_file_path: str = "",
):
    """Calls 'dvc repro' for either all stages or a subset.
    Redirects stdout and stderr to the specified log_file_path.
    """
    logger = get_run_logger()
    logger.info("Running DVC repro")
    base_cmd = ["dvc", "repro"]
    if pipeline:
        base_cmd.append("-P")
        logger.info("Pipeline mode is ON")
    if force:
        base_cmd.append("--force")
        logger.info("Force mode is ON")

    if not stages:
        logger.info("No specific stages => entire pipeline")
        with open(log_file_path, "a") as f:
            subprocess.run(base_cmd, stdout=f, stderr=subprocess.STDOUT, check=True)
    else:
        logger.info("Repro only these stages: %s", stages)
        for s in stages:
            cmd = [*base_cmd, s]
            with open(log_file_path, "a") as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=True)


@flow(name="DVC Orchestration Flow")
def dvc_flow(
    log_file_path: str,
    stages_list: Any,
    search_path: str,
    template_name: str,
    dvc_yaml_file_path: str,
    stages_to_run: list[str] | None = None,
    force_run: bool = False,
    pipeline_run: bool = False,
    allow_dvc_changes: bool = False,
    skip_generation: bool = False,
):
    """Orchestration flow that:
    1) Sets environment vars
    2) Ensures DVC is clean
    3) Optionally generates dvc.yaml
    4) Runs 'dvc repro'.
    """
    logger = get_run_logger()
    logger.info("Flow start")
    set_environment_vars()

    with open(log_file_path, "w") as f:
        f.write(log_file_path + "\n")

    top_level = (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode()
        .strip()
    )
    os.chdir(top_level)

    ensure_dvc_is_clean()

    if not skip_generation:
        generate_dvc_yaml(
            stages_list=stages_list,
            search_path=search_path,
            template_name=template_name,
            dvc_yaml_file_path=dvc_yaml_file_path,
            allow_dvc_changes=allow_dvc_changes,
        )
    else:
        logger.info("Skipping generation of new dvc.yaml")

    run_dvc_repro(
        stages=stages_to_run,
        force=force_run,
        pipeline=pipeline_run,
        log_file_path=log_file_path,
    )
    logger.info("Flow done")


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def main(cfg: RootConfig):
    logger = setup_logging(cfg)

    logging.getLogger("prefect").propagate = True
    logging.getLogger("prefect").setLevel(cfg.logging_utils.level)

    logger.info("Reading config, validating user stages")
    defined_stages = [stage.name for stage in cfg.pipeline.stages]
    user_stages = cfg.get("stages_to_run", [])

    invalid = [s for s in user_stages if s not in defined_stages]
    if invalid:
        valid_str = ", ".join(defined_stages)
        logger.error("Invalid stage(s): %s. Valid stage(s): %s", invalid, valid_str)
        msg = f"Invalid stage(s) requested: {invalid}. Valid stages: {valid_str}"
        raise RuntimeError(
            msg,
        )

    logger.info("User stages valid")

    stages_list = cfg.pipeline.stages
    search_path = cfg.pipeline.search_path
    template_name = cfg.pipeline.template_name
    dvc_yaml_file_path = cfg.pipeline.dvc_yaml_file_path
    log_file_path = cfg.pipeline.log_file_path
    force_run = cfg.pipeline.force_run
    pipeline_run = cfg.pipeline.pipeline_run
    allow_dvc_changes = cfg.pipeline.allow_dvc_changes
    skip_generation = cfg.pipeline.skip_generation

    log_function_call(
        dvc_flow(
            log_file_path=log_file_path,
            stages_list=stages_list,
            search_path=search_path,
            template_name=template_name,
            dvc_yaml_file_path=dvc_yaml_file_path,
            stages_to_run=user_stages,
            force_run=force_run,
            pipeline_run=pipeline_run,
            allow_dvc_changes=allow_dvc_changes,
            skip_generation=skip_generation,
        ),
    )


if __name__ == "__main__":
    main()
