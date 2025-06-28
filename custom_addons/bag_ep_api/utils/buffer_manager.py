class BufferManager:
	_internal_storage = {}  # Structure: {(user_id, key): item}
	
	
	@classmethod
	def get(cls, user_id, key = None):
		"""Public access to cached data per user."""
		if key is None:
			return {
				key: value
				for (uid, key), value in cls._internal_storage.items()
				if uid == user_id
				}
		
		else:
			return cls._internal_storage.get((user_id, key))
	
	
	@classmethod
	def set(cls, user_id, key, item):
		"""Store value for specific user and key."""
		cls._internal_storage[(user_id, key)] = item
	
	
	@classmethod
	def clear(cls, user_id = None, key = None):
		"""Clear specific item or entire buffer, per user if provided."""
		if user_id is not None and key is not None:
			# Clear a key for this user
			cls._internal_storage.pop((user_id, key), None)
		
		elif user_id is not None:
			# Clear all keys for this user
			keys_to_remove = [key for key in cls._internal_storage if key[0] == user_id]
			for key in keys_to_remove:
				cls._internal_storage.pop(key, None)
		
		else:
			# Clear the entire cache for all users.
			cls._internal_storage = {}
