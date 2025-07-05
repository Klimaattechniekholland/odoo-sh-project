import time
import logging
import httpx
from functools import wraps
from odoo import fields, http, api, models, SUPERUSER_ID
from odoo.http import request


_logger = logging.getLogger(__name__)


class Sales5APIHandler(http.Controller):
	BASE_URL = "https://your-api-url.com"  # Replace with actual URL
	
	
	@staticmethod
	def token_required(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			auth_header = request.httprequest.headers.get('Authorization', '')
			if not auth_header.startswith('Bearer '):
				return request.make_json_response(
					{
						'status': 'error',
						'message': 'Missing or invalid Authorization header'
						}, status = 401
					)
			
			token = auth_header.replace('Bearer ', '').strip()
			company = request.env.company
			
			expected_token = company.sales5_api_token
			if token != expected_token:
				return request.make_json_response(
					{
						'status': 'error',
						'message': 'Invalid API token'
						}, status = 401
					)
			
			return func(*args, **kwargs)
		
		
		return wrapper







# Automatic Token Fetch on System Startup
def post_init_hook(cr, registry):
	env = api.Environment(cr, SUPERUSER_ID, {})
	companies = env['res.company'].search([])
	token_manager = env['sales5.token.manager']

	for company in companies:
		try:
			_logger.info(f"[Sales5] Initializing token for company '{company.name}'")
			token_manager._get_api_token(company)
			_logger.info(f"[Sales5] Token initialized for '{company.name}'")
		except Exception as e:
			_logger.warning(f"[Sales5] Token initialization failed for '{company.name}': {str(e)}")
