import re
from odoo import _

from odoo.exceptions import UserError


def parse_full_house_number(full_house_number, warnings = None):
	"""
	Parses a full_house_number string into (number, letter, addition).
	Appends warnings if parsing fails.
	"""
	warnings = warnings or []
	
	if not full_house_number:
		return None, None, None
	
	try:
		house_number, house_letter, house_number_addition = _parse_full_house_number(full_house_number)
		return house_number, house_letter, house_number_addition
	
	except UserError as e:
		warnings.append(f"ZIP -- Invalid House Number Format '{str(e)}'")
		return None, None, None


def _parse_full_house_number(full_house_number):
	pattern = re.compile(r"^(\d+)([A-Za-z]?)(?:-(\d+))?$")
	match = pattern.match(full_house_number.strip())
	if not match:
		raise UserError(_("Invalid format. Use e.g. '70', '70A', '70-1', or '70A-1'."))
	
	return (
		int(match.group(1)),
		match.group(2) if match.group(2) else None,
		int(match.group(3)) if match.group(3) else None
		)
