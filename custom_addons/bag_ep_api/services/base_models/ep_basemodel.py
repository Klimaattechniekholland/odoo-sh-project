from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EpDataSchema(BaseModel):
    registration_date: Optional[datetime] = Field(default=None, alias='Registratiedatum')
    recording_date: Optional[datetime] = Field(default=None, alias='Opnamedatum')
    valid_until: Optional[datetime] = Field(default=None, alias='Geldig_tot')
    certificate_holder: str = Field(default="", alias='Certificaathouder')
    type_of_recording: str = Field(default="", alias='Soort_opname')
    status: str = Field(default="unknown", alias='Status')
    calculation_type: str = Field(default="", alias='Berekeningstype')
    based_on_reference_building: bool = Field(default=False, alias='Op_basis_van_referentiegebouw')
    building_class: str = Field(default="", alias='Gebouwklasse')
    building_type: str = Field(default="", alias='Gebouwtype')
    building_subtype: str = Field(default="", alias='Gebouwsubtype')
    postal_code: str = Field(default="", alias='Postcode')
    house_number: int = Field(default=0, alias='Huisnummer')
    house_letter: str = Field(default="", alias='Huisletter')
    house_number_addition: int = Field(default=0, alias='Huisnummertoevoeging')
    bag_residence_id: str = Field(default="", alias='BAGVerblijfsobjectID')
    bag_building_ids: List[str] = Field(default_factory=list, alias='BAGPandIDs')
    construction_year: int = Field(default=0, alias='Bouwjaar')
    usable_area_thermal_zone: float = Field(default=0.0, alias='Gebruiksoppervlakte_thermische_zone')
    usable_area: float = Field(default=0.0, alias='Gebruiksoppervlakte')
    compactness: float = Field(default=0.0, alias='Compactheid')
    energy_label: str = Field(default="", alias='Energieklasse')
    energy_demand: float = Field(default=0.0, alias='Energiebehoefte')
    primary_fossil_energy: float = Field(default=0.0, alias='PrimaireFossieleEnergie')
    primary_fossil_energy_emg_default: float = Field(default=0.0, alias='Primaire_fossiele_energie_EMG_forfaitair')
    share_renewable_energy: float = Field(default=0.0, alias='Aandeel_hernieuwbare_energie')
    temperature_exceedance: float = Field(default=0.0, alias='Temperatuuroverschrijding')
    heat_demand: float = Field(default=0.0, alias='Warmtebehoefte')
    calculated_co2_emission: float = Field(default=0.0, alias='BerekendeCO2Emissie')
    calculated_energy_consumption: float = Field(default=0.0, alias='BerekendeEnergieverbruik')

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }



