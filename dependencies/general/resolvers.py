import os
import subprocess

from omegaconf import OmegaConf


def shell(cmd: str) -> str:  # line comment changed
    return subprocess.check_output(
        cmd,
        shell=True,
        text=True,
    ).strip()  # line comment changed


OmegaConf.register_new_resolver("shell", shell)

# Then in your YAML config:
# timestamp: ${shell:date +%Y-%m-%d_%H-%M-%S}

OmegaConf.register_new_resolver("join", lambda *args: os.path.join(*args))
