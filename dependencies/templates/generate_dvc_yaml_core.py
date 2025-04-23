# dependencies/templates/generate_dvc_yaml_core.py
from __future__ import annotations

import logging
import os

import jinja2
from logging_utils.log_function_call import log_function_call

logger = logging.getLogger(__name__)


@log_function_call
def generate_dvc_yaml_core(
    stages_list: list,
    search_path: str,
    template_name: str,
    dvc_yaml_file_path: str,
    plots_list: list | None = None,
) -> None:
    logger.info("Entering function 'generate_dvc_yaml_core'")
    loader = jinja2.FileSystemLoader(searchpath=search_path)
    env = jinja2.Environment(loader=loader, autoescape=False)
    template = env.get_template(template_name)

    rendered = template.render(stages=stages_list, plots=plots_list)

    with open(dvc_yaml_file_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    if os.path.exists(dvc_yaml_file_path):
        logger.info("Success: 'generate_dvc_yaml_core'")


if __name__ == "__main__":
    import sys

    import hydra
    from omegaconf import DictConfig

    sys.argv = [sys.argv[0], "pipeline=orchestrate_dvc_flow"]

    @hydra.main(version_base=None, config_path="../../configs", config_name="config")
    def main(cfg: DictConfig):
        stages_list = cfg.pipeline.stages
        search_path = cfg.pipeline.search_path
        template_name = cfg.pipeline.template_name
        dvc_yaml_file_path = cfg.pipeline.dvc_yaml_file_path
        plots_list = cfg.pipeline.get("plots", None)
        generate_dvc_yaml_core(
            stages_list,
            search_path,
            template_name,
            dvc_yaml_file_path,
            plots_list=plots_list,
        )

    main()
