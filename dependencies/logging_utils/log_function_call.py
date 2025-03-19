import logging
from functools import wraps


def log_function_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        function_name = fn.__name__
        logger.debug("Entering function: %s", function_name)
        try:
            result = fn(*args, **kwargs)
            logger.debug("Exiting function: %s, status: success", function_name)
            return result
        except Exception as e:
            logger.error("Function: %s failed with exception: %s", function_name, e)
            raise

    return wrapper
