def pick_year(value):
	if isinstance(value, list):
		nums = [
			int(s) for s in (value or [])
			if isinstance(s, str) and s.strip().lstrip('-').isdigit()
			]
		return (max(nums)) if nums else 0
	
	if isinstance(value, int):
		return value
	
	return None


def filter_model_fields(env, model_name, raw_values: dict):
	valid_fields = env[model_name].fields_get().keys()
	
	# Define per-field transformation rules
	field_transformations = {
		"construction_year": pick_year,
		"bag_building_ids": lambda value: value if isinstance(value, list) else [value],
		}
	
	cleaned_values = {}
	
	for field_name, raw_value in raw_values.items():
		if field_name not in valid_fields:
			continue
		
		if field_name in field_transformations:
			try:
				cleaned_values[field_name] = field_transformations[field_name](raw_value)
			
			except Exception:
				cleaned_values[field_name] = None  # Optional: log the error
		
		else:
			cleaned_values[field_name] = raw_value
	
	return cleaned_values
