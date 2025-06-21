from cachetools import LRUCache
from sys import getsizeof
import logging


_logger = logging.getLogger(__name__)

MAX_CACHE_SIZE = 5 * 1024 * 1024  # 5MB


def get_entry_size(entry):
	try:
		return getsizeof(entry)
	
	except Exception:
		return 1024  # fallback size


def create_lru_cache():
	return LRUCache(maxsize = MAX_CACHE_SIZE, getsizeof = get_entry_size)
