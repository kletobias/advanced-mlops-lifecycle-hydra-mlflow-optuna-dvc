import logging
import subprocess

logger = logging.getLogger(__name__)


def get_repo_root() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .strip()
        .decode()
    )


def anonymize_path(file_path: str) -> str:
    root = get_repo_root()
    if file_path.startswith(root):
        return "." + file_path[len(root) :]
    return file_path
