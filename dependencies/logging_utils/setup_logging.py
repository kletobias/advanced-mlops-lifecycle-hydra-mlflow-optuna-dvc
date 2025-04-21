import logging
import sys
from functools import cache
from pathlib import Path

try:
    import colorlog
except ImportError:
    colorlog = None

from dependencies.config_schemas.RootConfig import RootConfig
from dependencies.general.mkdir_if_not_exists import mkdir_
from dependencies.logging_utils.log_function_call import log_function_call

_REPO_ROOT = Path(__file__).resolve()
while not (_REPO_ROOT / ".git").exists() and _REPO_ROOT.parent != _REPO_ROOT:
    _REPO_ROOT = _REPO_ROOT.parent


@cache
def _rel(p: str) -> str:
    try:
        return str(Path(p).resolve().relative_to(_REPO_ROOT))
    except Exception:
        return p


_old_factory = logging.getLogRecordFactory()


def _factory(*args, **kwargs):
    r = _old_factory(*args, **kwargs)
    r.pathname = _rel(r.pathname)
    return r


logging.setLogRecordFactory(_factory)


@log_function_call
def setup_logging(cfg: RootConfig) -> logging.Logger:
    log_directory_path = cfg.logging_utils.log_directory_path
    log_file_path = cfg.logging_utils.log_file_path
    formatter_str = cfg.logging_utils.formatter
    level = cfg.logging_utils.level

    mkdir_(log_directory_path)

    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger

    logger.setLevel(level)

    fh = logging.FileHandler(log_file_path)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(formatter_str))
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    if colorlog and sys.stdout.isatty():
        log_colors = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        }
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s" + formatter_str,
            log_colors=log_colors,
            reset=True,
        )
        sh.setFormatter(color_formatter)
    else:
        sh.setFormatter(logging.Formatter(formatter_str))
    logger.addHandler(sh)

    return logger
