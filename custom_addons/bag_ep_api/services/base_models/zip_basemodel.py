from typing import Optional
from pydantic import BaseModel, ConfigDict


class ZipData(BaseModel):
	postcode: str
	huisnummer: str
	straat: Optional[str]
	buurt: Optional[str]
	wijk: Optional[str]
	woonplaats: Optional[str]
	gemeente: Optional[str]
	provincie: Optional[str]
	latitude: Optional[float]
	longitude: Optional[float]
	
	model_config = ConfigDict(
		extra = "allow",
		populate_by_name = True
		)
