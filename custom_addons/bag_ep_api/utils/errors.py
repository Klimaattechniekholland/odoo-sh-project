from enum import Enum


class BagApiError(Enum):
	NoError = "NoError"
	NotFound = "NotFound"
	HuisletterNotAvailable = "HuisletterNotAvailable"
	Nojson = "NoJson"
	SystemError = "SystemError"
	
	def __str__(self):
		return self.value
