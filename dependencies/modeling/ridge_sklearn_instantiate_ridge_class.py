import logging

from sklearn.linear_model import Ridge

logger = logging.getLogger(__name__)


def ridge_sklearn_instantiate_ridge_class(final_params: dict) -> Ridge:
    kwargs_instantiate_ridge_class = final_params

    return Ridge(**kwargs_instantiate_ridge_class)
