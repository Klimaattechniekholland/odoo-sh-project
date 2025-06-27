# base_resolver.py

import logging

from odoo.addons.bag_ep_api.utils.cache import create_lru_cache


_logger = logging.getLogger(__name__)


class BaseEpResolver:
	_caches_by_company = {}
	
	
	def __init__(self, partner, env = None):
		self.partner = partner
		self.env = env or partner.env
		self.client = self._init_client()
	
	
	def get(self, warnings = None, force_refresh = False):
		warnings = warnings or []
		key = self._cache_key()
		cache = self._get_cache()
		
		if not force_refresh and key in cache:

			return cache[key], warnings
		
		result = self._fetch(warnings)
		if result is not None:
			cache[key] = result
		
		return result, warnings
	
	
	def clear_cache(self):
		self._get_cache().pop(self._cache_key(), None)
	
	
	def clear_partner_cache(self):
		prefix = self._source_prefix()
		pid = self.partner.id
		
		keys_to_remove = [
			k for k in self._get_cache()
			if k[0] == prefix and k[1] == pid
			]
		
		for k in keys_to_remove:
			self._get_cache().pop(k, None)

	
	def _get_cache(self):
		company_id = self.env.company.id
		if company_id not in self._caches_by_company:
			self._caches_by_company[company_id] = create_lru_cache()
		return self._caches_by_company[company_id]
	
	
	def _cache_key(self):
		return (
			self._source_prefix(),
			self.partner.id or 0,
			(self.partner.zip or "").replace(" ", "").upper(),
			self.partner.full_house_number or "",
			)
	
	
	def _fetch(self, warnings):
		partner = self.partner
		if not partner.zip or not partner.full_house_number:
			return None
		
		try:
			response = self._call_api(partner)
			if not response:
				return None
			
			_logger.info(f"[{self._source_prefix()}] Autofill completed for {partner.name}.")
			return response
		
		except Exception as e:
			_logger.warning(f"[{self._source_prefix()}] API call failed for {partner.name}: {e}")
			warnings.append(
				f"{self._source_prefix()} — fout bij ophalen data voor postcode '{partner.zip}' "
				f"en huisnummer '{partner.full_house_number}'."
				)
			return None
	
	
	# Abstract methods to implement in subclass:
	def _init_client(self):
		raise NotImplementedError
	
	
	def _call_api(self, partner):
		raise NotImplementedError
	
	
	def _source_prefix(self):
		raise NotImplementedError
