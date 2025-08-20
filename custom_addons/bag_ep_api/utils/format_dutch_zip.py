import re

def format_dutch_zip(zipcode: str, with_space: bool = True) -> str:
    """
    Formats Dutch ZIP code to '1234 AB' or '1234AB'.
    - Removes spaces
    - Uppercases letters
    - Returns cleaned fallback if invalid
    """
    if not zipcode:
        return ''

    cleaned = zipcode.replace(" ", "").upper()
    match = re.match(r"^(\d{4})([A-Z]{2})$", cleaned)
    if match:
        if with_space:
            return f"{match.group(1)} {match.group(2)}"
        else:
            return f"{match.group(1)}{match.group(2)}"
    else:
        return ''  # invalid format
