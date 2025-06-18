from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class Link(BaseModel):
	href: HttpUrl


class PandLink(BaseModel):
	href: HttpUrl


class Links(BaseModel):
	self: Link
	openbareRuimte: Optional[Link]
	nummeraanduiding: Optional[Link]
	woonplaats: Optional[Link]
	adresseerbaarObject: Optional[Link]
	panden: Optional[List[PandLink]]


class Geometrie(BaseModel):
	type: str
	coordinates: List[float]


class AdresseerbaarObjectGeometrie(BaseModel):
	punt: Geometrie


class Adres(BaseModel):
	openbareRuimteNaam: Optional[str]
	korteNaam: Optional[str]
	
	huisnummer: int
	# house_number: int = Field(default = 0, alias = 'huisnummer')
	# huisletter:Optional[str]
	# house_letter: str = Field(default = "", alias = 'huisletter')
	# huisnummertoevoeging:Optional[int]
	# house_number_addition: int = Field(default = 0, alias = 'huisnummertoevoeging')
	# postcode: str
	postal_code: str = Field(default = "", alias = 'postcode')
	
	woonplaatsNaam: Optional[str]
	nummeraanduidingIdentificatie: str
	openbareRuimteIdentificatie: Optional[str]
	woonplaatsIdentificatie: Optional[str]
	adresseerbaarObjectIdentificatie: str
	pandIdentificaties: Optional[List[str]]
	adresregel5: Optional[str]
	adresregel6: Optional[str]
	typeAdresseerbaarObject: Optional[str]
	adresseerbaarObjectGeometrie: Optional[AdresseerbaarObjectGeometrie]
	adresseerbaarObjectStatus: Optional[str]
	gebruiksdoelen: Optional[List[str]]
	
	# oppervlakte: Optional[int]
	usable_area: float = Field(default = 0.0, alias = 'oppervlakte')
	# oorspronkelijkBouwjaar: Optional[List[str]]
	construction_year:  Optional[List[str]] = Field(default = 0, alias = 'oorspronkelijkBouwjaar')
	
	pandStatussen: Optional[List[str]]
	_links: Links


class Embedded(BaseModel):
	adressen: List[Adres]


class RootLinks(BaseModel):
	self: Link


class AddressResponse(BaseModel):
	embedded: Embedded = Field(alias = "_embedded")
	links: RootLinks = Field(alias = "_links")
	
	model_config = ConfigDict(
		extra = "allow",
		populate_by_name = True
		)
