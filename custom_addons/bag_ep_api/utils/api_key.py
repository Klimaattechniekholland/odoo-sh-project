import logging
import os

_logger = logging.getLogger(__name__)

# =========================================================
# naming api_keys.bag, api_keys.EP and
# example: bag_api_key = get_api_key(env, 'api_keys.bag', env_var='BAG_API_KEY')
# _logger.info("Using BAG Key: %s", redact_key(bag_api_key))
# ========================================================

def get_api_key(env, param_key, env_var=None, allow_env_fallback=True):
    key = env['ir.config_parameter'].sudo().get_param(param_key)
    if not key and allow_env_fallback and env_var:
        key = os.environ.get(env_var)
        if key:
            _logger.warning("Using fallback from environment variable %s", env_var)
    if not key:
        raise ValueError(f"API key not found. Set in config param '{param_key}' or env '{env_var}'.")
    return key

def redact_key(key, visible=4):
    if not key or len(key) <= visible:
        return "****"
    return f"{key[:visible]}...****"
