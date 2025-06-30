import httpx

from odoo import http
from odoo.http import request

def token_required(func):
    def wrapper(*args, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        expected_token = request.env['ir.config_parameter'].sudo().get_param('sales5.api.token')

        if not token or token.replace('Bearer ', '') != expected_token:
            return {'status': 'error', 'message': 'Invalid or missing API token'}

        return func(*args, **kwargs)
    return wrapper

def _get_api_token(self):
    param_model = self.env['ir.config_parameter'].sudo()
    token = param_model.get_param('sales5.api.token')

    # Optional: track expiration timestamp
    expires_at = param_model.get_param('sales5.api.token.expires_at')

    if not token or (expires_at and float(expires_at) < time.time()):
        _logger.info("[Sales5] Token expired or missing, fetching new token")
        token = self._refresh_api_token()
        param_model.set_param('sales5.api.token', token)
        param_model.set_param('sales5.api.token.expires_at', time.time() + 3600)  # Example: 1 hour validity

    return token

def _refresh_api_token(self):
    # Example token request - replace with real implementation
    url = f"{self.BASE_URL}/auth/token"
    response = httpx.post(url, data={"client_id": "XXX", "client_secret": "YYY"})
    response.raise_for_status()
    return response.json().get("access_token")
