import time
import logging
import httpx
from odoo import models

_logger = logging.getLogger(__name__)

class Sales5TokenManager(models.AbstractModel):
    _name = 'sales5.token.manager'
    _description = 'Sales5 API Token Manager'

    def _get_api_token(self, company=None):
        if not company:
            company = self.env.company

        token = company.sales5_api_token
        expires_at = company.sales5_token_expires_at

        if not token or (expires_at and expires_at < time.time()):
            _logger.info(f"[Sales5] Token expired or missing for company '{company.name}', fetching new token")
            token_data = self._refresh_api_token(company)

            token = token_data.get("access_token")
            if not token:
                _logger.error(f"[Sales5] Failed to fetch token for company '{company.name}'")
                raise Exception("Unable to retrieve API token")

            company.write({
                'sales5_api_token': token,
                'sales5_token_expires_at': time.time() + token_data.get("expires_in", 3600),
                'sales5_refresh_token': token_data.get("refresh_token") or company.sales5_refresh_token
            })

        return token

    def _refresh_api_token(self, company):
        if not company.sales5_client_id or not company.sales5_client_secret:
            _logger.error(f"[Sales5] Missing client credentials for company '{company.name}'")
            raise Exception("Sales5 API credentials not configured")

        url = "https://your-api-url.com/auth/token"

        if company.sales5_refresh_token:
            _logger.info(f"[Sales5] Refreshing token for '{company.name}'")
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": company.sales5_refresh_token,
                "client_id": company.sales5_client_id,
                "client_secret": company.sales5_client_secret
            }
        else:
            _logger.info(f"[Sales5] Using client credentials for '{company.name}'")
            payload = {
                "grant_type": "client_credentials",
                "client_id": company.sales5_client_id,
                "client_secret": company.sales5_client_secret
            }

        response = httpx.post(url, data=payload, timeout=10)
        response.raise_for_status()

        return response.json()

