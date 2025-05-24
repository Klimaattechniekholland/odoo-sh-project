import requests

class EpOnlineClient:
    """
    Client for RVO EP-Online (energy labels) service.
    """
    BASE_URL = "https://epbdwebservices.rvo.nl/energielabel"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_by_address(self, postcode, huisnummer, huisletter='', toevoeging=''):
        """
        Query EP-Online by address components.
        """
        params = {
            'postcode': postcode,
            'huisnummer': huisnummer,
            'huisletter': huisletter or '',
            'huisnummertoevoeging': toevoeging or '',
            'apikey': self.api_key,
        }
        try:
            res = requests.get(self.BASE_URL + "/address", params=params, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception:
            return None
        return None

    def get_by_bag(self, verblijfsobject_id):
        """
        Query EP-Online using a BAG Verblijfsobject ID.
        """
        params = {'bagverblijfsobjectid': verblijfsobject_id, 'apikey': self.api_key}
        try:
            res = requests.get(self.BASE_URL + "/bagid", params=params, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception:
            return None
        return None
