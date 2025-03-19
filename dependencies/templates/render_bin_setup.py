# dependencies/templates/make_default_j200_setup.py
import jinja2
from omegaconf import DictConfig


def make_setup(cfg: DictConfig) -> str:
    """# CONFIG: Add new template file paths
    Loads the Jinja2 template "default.j2" (located in 'templates/setup/default.j2',
    or wherever cfg.templates.template_file_path points to), then renders it with values
    from the Hydra config, returning the rendered text.
    """
    template_directory_path = cfg.templates.insert_template_directory_path
    template_file_name = cfg.templates.insert_template_file_name
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_directory_path))

    template = env.get_template(template_file_name)

    version = cfg.templates.insert_data_version
    base_name = cfg.templates.insert_script_base_name
    project_section = cfg.templates.insert_project_section

    # Render with as many variables as you need
    return template.render(
        version=version,
        base_name=base_name,
        project_section=project_section,
    )
