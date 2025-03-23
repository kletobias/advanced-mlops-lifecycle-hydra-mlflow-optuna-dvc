# dependencies/templates/generate_dvc_yaml_core.py
import logging
import os
import time
from typing import List

import jinja2

logger = logging.getLogger(__name__)


def generate_dvc_yaml_core(
    stages_list: List,
    search_path: str,
    template_name: str,
    dvc_yaml_file_path: str,
) -> None:
    logger.info("Entering function 'generate_dvc_yaml_core'")
    loader = jinja2.FileSystemLoader(searchpath=search_path)
    env = jinja2.Environment(loader=loader, autoescape=False)
    template = env.get_template(template_name)

    rendered = template.render(stages=stages_list)

    with open(dvc_yaml_file_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    if os.path.exists(dvc_yaml_file_path):
        logger.info(
            "Exiting function 'generate_dvc_yaml_core', most recent change: dvc.yaml %s",
            time.time() - os.path.getmtime(dvc_yaml_file_path),
        )

if __name__ == "__main__":
    from omegaconf import DictConfig
    import hydra
    import sys
    sys.argv = [
        sys.argv[0],
        'pipeline=orchestrate_dvc_flow'
    ]
    @hydra.main(version_base=None, config_path='../../configs',config_name='config')
    def main(cfg:DictConfig):
        stages_list = cfg.pipeline.stages
        search_path = cfg.pipeline.search_path
        template_name = cfg.pipeline.template_name
        dvc_yaml_file_path = cfg.pipeline.dvc_yaml_file_path
        generate_dvc_yaml_core(stages_list,search_path,template_name,dvc_yaml_file_path)

    main()
