# base_resolver.py

import logging


_logger = logging.getLogger(__name__)


class BaseEpResolver:
	_cache = {}
	
	
	def __init__(self, partner, env = None):
		self.partner = partner
		self.env = env or partner.env
		self.client = self._init_client()
	
	
	def get(self, warnings = None, force_refresh = False):
		warnings = warnings or []
		key = self._cache_key()
		
		if not force_refresh and key in self._cache:
			return self._cache[key], warnings
		
		result = self._fetch(warnings)
		if result is not None:
			self._cache[key] = result
		
		return result, warnings
	
	
	def clear_cache(self):
		self._cache.pop(self._cache_key(), None)
	
	
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
