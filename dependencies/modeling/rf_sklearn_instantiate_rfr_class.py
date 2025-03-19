import logging
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)

def rf_sklearn_instantiate_rfr_class(final_params:dict,rfr_options:dict) -> RandomForestRegressor:
    kwargs_instantiate_rfr_class = final_params.copy()
    kwargs_instantiate_rfr_class.update(rfr_options)
    logger.debug("Merged dictionaries 'final_params', and 'rfr_options'")

    model = RandomForestRegressor(
        **kwargs_instantiate_rfr_class
    )
    return model
