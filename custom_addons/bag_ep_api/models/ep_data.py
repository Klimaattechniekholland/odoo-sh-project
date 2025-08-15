from odoo import models, fields, _


class EpData(models.Model):
	_name = 'ep.data'
	_description = 'EP Information'
	
	_sql_constraints = [
		('unique_partner', 'unique(partner_id)', 'Each partner can have only one EP record.')
		]
	
	partner_id = fields.Many2one(
		comodel_name = 'res.partner',
		string = "Partner",
		ondelete = 'cascade',
		required = True,
		index = True,
		)
	
	registration_date = fields.Datetime(string = _("Registration Date"))
	recording_date = fields.Datetime(string = _("Recording Date"))
	valid_until = fields.Datetime(string = _("Valid Until"))
	certificate_holder = fields.Char(string = _("Certificate Holder"))
	recording_type = fields.Char(string = _("Recording Type"))
	status = fields.Char(string = _("Status"))
	calculation_type = fields.Char(string = _("Calculation Type"))
	based_on_reference_building = fields.Boolean(string = _("Based on Reference Building"))
	building_class = fields.Char(string = _("Building Class"))
	building_type = fields.Char(string = _("Building Type"))
	building_subtype = fields.Char(string = _("Building Subtype"))
	postal_code = fields.Char(string = _("Postal Code"))
	house_number = fields.Integer(string = _("House Number"))
	house_letter = fields.Char(string = _("House Letter"))
	house_number_addition = fields.Integer(string = _("House_Number Addition"))
	bag_residence_id = fields.Char(string = _("BAG Residence ID"))
	bag_building_ids = fields.Json(string = _("BAG Building IDs"))
	construction_year = fields.Integer(string = _("Construction Year"))
	usable_area_thermal_zone = fields.Float(string = _("Usable Area - Thermal Zone"))
	usable_area = fields.Float(string = _("Usable Area"))
	compactness = fields.Float(string = _("Compactness"))
	energy_label = fields.Char(string = _("Energy Label"))
	energy_demand = fields.Float(string = _("Energy Demand"))
	primary_fossil_energy = fields.Float(string = _("Primary Fossil Energy"))
	primary_fossil_energy_emg_default = fields.Float(string = _("Primary Fossil Energy EMG Default"))
	renewable_energy_share = fields.Float(string = _("Renewable Energy Share"))
	temperature_exceedance = fields.Float(string = _("Temperature Exceedance"))
	heat_demand = fields.Float(string = _("Heat Demand"))
	calculated_co2_emission = fields.Float(string = _("Calculated CO₂ Emission"))
	calculated_energy_consumption = fields.Float(string = _("Calculated Energy Consumption"))

