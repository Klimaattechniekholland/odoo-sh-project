# -*- coding: utf-8 -*-

import re

def parse_house_number(house_number_str):
    """
    Parse a Dutch house number string into components:
    Examples:
        70-1 -> (70, '1', None)
        89A -> (89, None, 'A')
    Returns (huisnummer, toevoeging, letter).
    """
    if not house_number_str:
        return None, None, None
    house_number_str = house_number_str.strip()
    match = re.match(r'^(?P<number>\d+)(?:-?(?P<addition>\d+))?(?P<letter>[A-Za-z]?)$', house_number_str)
    if not match:
        return house_number_str, None, None
    number = int(match.group('number'))
    addition = match.group('addition') or None
    letter = match.group('letter') or None
    return number, addition, letter
