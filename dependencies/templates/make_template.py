# dependencies/templates/make_template.py
import logging

import jinja2

from dependencies.config_schemas.RootConfig import RootConfig

logger = logging.getLogger(__name__)


def make_template(cfg: RootConfig):
    assert sum(cfg.setup.final_template_options.values()) == 1, (
        "Invalid selection of final_template_options"
    )

    script_template_directory_path = cfg.setup.script_template_directory_path
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(script_template_directory_path),
    )
    template = env.get_template(cfg.setup.script_template_filename)
    return template.render(
        setup=cfg.setup,
        version=cfg.data_versions.data_version_input,
    )
