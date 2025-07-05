import logging

from .bag_api_client import BagApiResolver
from .ep_api_client import EpApiResolver
from .zip_api_client import ZipApiResolver


_logger = logging.getLogger(__name__)


class ResolverManager:
	
	def __init__(self, partner, env = None):
		self.partner = partner
		self.env = env or partner.env
		self._warnings = []
		self._fetched_data = None
		self._bag_data = None
		self._parsed_data = None
	
	
	def resolve_zip(self, warnings = None, fields = False):
		self._warnings = warnings or []
		self._run_zip(fields)
		return self._parsed_data, self._warnings
	
	
	def resolve_bag_ep(self, warnings = None):
		self._warnings = warnings or []
		# Step – BAG Resolver
		self._run_bag()
		# Step – EP Resolver
		self._run_ep()
		return self._fetched_data, self._warnings
	
	
	def resolve_all(self, warnings = None, fields = False):
		self.resolve_zip(warnings, fields)
		self.resolve_bag_ep(warnings)
		return self._fetched_data, self._warnings
	
	
	def _run_zip(self, fields = False):
		if fields:
			ZipApiResolver(self.partner).clear_cache()
		
		zip_data, self._warnings = ZipApiResolver(self.partner).get(self._warnings)
		if zip_data and not self._warnings:
			self._parsed_data = ZipApiResolver(self.partner).values_from_data(zip_data)
			if fields:
				ZipApiResolver(self.partner).fields_from_data(zip_data)
			return self._parsed_data
		
		return None
	
	
	def _run_bag(self):
		if self._warnings:
			return
		
		# we fetch all adressen if there are more than one because of the number, letter, addition
		self._bag_data, self._warnings = BagApiResolver(self.partner).get(self._warnings)
		
		if self._bag_data and not self._warnings:
			# get only one, first address
			self._bag_data, self._warnings = BagApiResolver(self.partner).apply_from_data(
				self._bag_data, self._warnings
				)
			self._fetched_data = self._bag_data
	
	
	def _run_ep(self, ):
		if self._warnings:
			return
		
		self._fetched_data, self._warnings = EpApiResolver(self.partner).get(self._warnings)
		if self._warnings:
			return
		
		self._fetched_data = EpApiResolver(self.partner).apply_from_data(self._fetched_data, self._bag_data)
