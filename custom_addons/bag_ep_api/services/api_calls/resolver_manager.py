import logging
from .zip_api_client import ZipApiResolver
from .bag_api_client import BagApiResolver
from .ep_api_client import EpApiResolver


_logger = logging.getLogger(__name__)


class ResolverManager:
	def __init__(self, partner, env = None):
		self.partner = partner
		self.env = env or partner.env
		self._warnings = []
		self._fetched_data = None
		self._bag_data = None
	
	
	def resolve_all(self, warnings = None):
		self._warnings = warnings or []
		
		self._format_house_number()
		
		# Step 1 – ZIP Resolver
		self._run_zip()
		
		# Step 2 – BAG Resolver
		self._run_bag()
		
		# Step 3 – EP Resolver
		self._run_ep()
		
		return self._fetched_data, self._warnings
	
	
	def _format_house_number(self):
		self.partner._full_house_number_format(self._warnings)
	
	
	def _run_zip(self):
		zip_data, self._warnings = ZipApiResolver(self.partner).get(self._warnings)
		if zip_data and not self._warnings:
			ZipApiResolver(self.partner).apply_from_data(zip_data)
	
	
	def _run_bag(self):
		if self._warnings:
			return
		
		# we fetch all adressen if there are more than one because of the number, letter, addition
		self._bag_data, self._warnings = BagApiResolver(self.partner).get(self._warnings)
		
		if self._bag_data and not self._warnings:
			# get only one, first address
			self._bag_data = BagApiResolver(self.partner).apply_from_data(self._bag_data)
			self._fetched_data = self._bag_data
	
	
	def _run_ep(self):
		if self._warnings:
			return
		
		self._fetched_data, self._warnings = EpApiResolver(self.partner).get(self._warnings)
		if self._warnings:
			return
			
		self._fetched_data = EpApiResolver(self.partner).apply_from_data(self._fetched_data, self._bag_data)
		