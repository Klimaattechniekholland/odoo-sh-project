import httpx
import logging
import time

_logger = logging.getLogger(__name__)

class Sales5Fetcher:

    BASE_URL = "https://external-system/api/sales5"

    def __init__(self, env):
        self.env = env
        self.token = self._get_api_token()

    def _get_api_token(self):
        return self.env['ir.config_parameter'].sudo().get_param('sales5.api.token')

    def fetch_sales5(self, order_id, max_retries=3):
        url = f"{self.BASE_URL}/{order_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        for attempt in range(1, max_retries + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    _logger.info(f"[Sales5] Attempt {attempt}: Fetching order {order_id}")
                    response = client.get(url, headers=headers)
                    response.raise_for_status()

                    data = response.json()
                    _logger.info(f"[Sales5] Success: Data received for order {order_id}")
                    _logger.debug(f"[Sales5] Response JSON: {data}")

                    return data  # Success

            except httpx.HTTPError as e:
                _logger.warning(f"[Sales5] Attempt {attempt} failed for order {order_id}: {e}")

                if attempt < max_retries:
                    time.sleep(2)  # Optional backoff between retries
                else:
                    _logger.error(f"[Sales5] All attempts failed for order {order_id}")

        return None  # All retries failed
