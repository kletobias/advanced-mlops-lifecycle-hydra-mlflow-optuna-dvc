# dependencies/templates/generate_dvc_yaml_core.py
from typing import List
import jinja2

from dependencies.general.mkdir_if_not_exists import mkdir_


def generate_dvc_yaml_core(
    stages_list: List,
    search_path: str,
    template_name: str,
    dvc_yaml_file_path: str,
    experiment_directory_path: str,
) -> None:
    mkdir_(experiment_directory_path)

    loader = jinja2.FileSystemLoader(searchpath=search_path)
    env = jinja2.Environment(loader=loader, autoescape=False)
    template = env.get_template(template_name)

    rendered = template.render(stages=stages_list)

    with open(dvc_yaml_file_path, "w", encoding="utf-8") as f:
        f.write(rendered)
