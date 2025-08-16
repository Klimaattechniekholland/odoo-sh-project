from odoo import _, api, fields, models


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
	
	# ----------------------------
	# Fields for EP-request
	# ----------------------------
	registration_date = fields.Datetime(string = _("Registration Date"), readonly = True)
	recording_date = fields.Datetime(string = _("Recording Date"), readonly = True)
	valid_until = fields.Datetime(string = _("Valid Until"))
	certificate_holder = fields.Char(string = _("Certificate Holder"), readonly = True)
	recording_type = fields.Char(string = _("Recording Type"), readonly = True)
	status = fields.Char(string = _("Status"), readonly = True)
	calculation_type = fields.Char(string = _("Calculation Type"), readonly = True)
	based_on_reference_building = fields.Boolean(string = _("Based on Reference Building"), readonly = True)
	building_class = fields.Char(string = _("Building Class"), readonly = True)
	building_type = fields.Char(string = _("Building Type"), readonly = True)
	building_subtype = fields.Char(string = _("Building Subtype"), readonly = True)
	postal_code = fields.Char(string = _("Postal Code"), readonly = True)
	house_number = fields.Integer(string = _("House Number"), readonly = True)
	house_letter = fields.Char(string = _("House Letter"), readonly = True)
	house_number_addition = fields.Integer(string = _("House_Number Addition"), readonly = True)
	bag_residence_id = fields.Char(string = _("BAG Residence ID"), readonly = True)
	bag_building_ids = fields.Json(string = _("BAG Building IDs"), readonly = True)
	construction_year = fields.Integer(string = _("Construction Year"), readonly = True)
	usable_area_thermal_zone = fields.Float(string = _("Usable Area - Thermal Zone"), readonly = True)
	usable_area = fields.Float(string = _("Usable Area"), readonly = True)
	compactness = fields.Float(string = _("Compactness"), readonly = True)
	energy_label = fields.Char(string = _("Energy Label"), readonly = True)
	energy_demand = fields.Float(string = _("Energy Demand"), readonly = True)
	primary_fossil_energy = fields.Float(string = _("Primary Fossil Energy"), readonly = True)
	primary_fossil_energy_emg_default = fields.Float(string = _("Primary Fossil Energy EMG Default"), readonly = True)
	renewable_energy_share = fields.Float(string = _("Renewable Energy Share"), readonly = True)
	temperature_exceedance = fields.Float(string = _("Temperature Exceedance"), readonly = True)
	heat_demand = fields.Float(string = _("Heat Demand"), readonly = True)
	calculated_co2_emission = fields.Float(string = _("Calculated CO₂ Emission"), readonly = True)
	calculated_energy_consumption = fields.Float(string = _("Calculated Energy Consumption"), readonly = True)
	
	# ----------------------------
	# Fields  for calculations
	# ----------------------------
	hdd_value = fields.Float(string = "HDD value (graaddagen)", default = 2700)
	indoor_temp = fields.Integer(string = "Indoor Temp. (°C)", default = 20)
	outdoor_design_temp = fields.Integer(string = "Outdoor Temp. (°C)", default = -10)
	margin_percent_kw = fields.Float(string = "Marge (%)", default = 10.0)
	full_load_hours = fields.Float(string = "Annual Full Load (h)", default = 1650.0)
	
	# ----------------------------
	# Computed: power  and specific power
	# -------------------------
	design_kw = fields.Float(
		string = "Design Power (kW)",
		compute = "_compute_design_ep_heat_loss",
		store = True,
		readonly = True,
		)
	
	design_heat_square_m2 = fields.Float(
		string = "Design Heat (W/m²)",
		compute = "_compute_design_heat_square_m2",
		store = True,
		readonly = True,
		)
	
	delta_t = fields.Float(
		string = "ΔT Design (K)",
		compute = "_compute_delta_t",
		store = True,
		readonly = True,
		help = "Temperature difference: indoor_temp - outdoor_design_temp",
		)
	
	annual_heat_consumption = fields.Float(
		string = "heta consumption",
		compute = "_compute_annual_heat_consumption",
		store = True,
		readonly = True,
		)
	
	design_ep_heat_loss_full_load = fields.Float(
		string = "Design Heat (kW) @ Full Load",
		compute = "_compute_design_ep_heat_loss_full_load",
		store = True,
		readonly = True,
		)
	
	# energy_demand_unit = fields.Selection(
	# 	[
	# 		("kwh_m2y", "kWh/m²·jr"),
	# 		("mj_m2y", "MJ/m²·jr"),
	# 		],
	# 	string = "Unit of Energy Demand",
	# 	default = "kwh_m2y",
	# 	required = True,
	# 	)
	
	@api.depends('energy_demand', 'usable_area_thermal_zone')
	def _compute_annual_heat_consumption(self):
		"""
		energy_demand: kWh per m²·year
		usable_area_thermal_zone: m²
		annual_heat_consumption = energy_demand * area  (kWh/yr)
		"""
		for rec in self:
			try:
				kwh = (rec.energy_demand or 0.0) * (rec.usable_area_thermal_zone or 0.0)
				
			except Exception:
				kwh = 0.0
				
			rec.annual_heat_consumption = kwh
	
	
	@api.depends("indoor_temp", "outdoor_design_temp")
	def _compute_delta_t(self):
		""" ΔT = indoor_temp - outdoor_design_temp
		        Always assign a value for every record.
		"""
		for rec in self:
			try:
				inside = rec.indoor_temp if rec.indoor_temp is not None else 20
				outside = rec.outdoor_design_temp if rec.outdoor_design_temp is not None else -10
				rec.delta_t = float(inside) - float(outside)
			
			except Exception:
				rec.delta_t = 0.0  # safe fallback
	
	
	@api.depends('hdd_value', 'delta_t', 'margin_percent_kw')
	def _compute_design_ep_heat_loss(self, is_kw = True):
		"""
        Design heat loss:
            base = (annual_heat_consumption * ΔT) / (HDD * 24)
            design_kw = base * (1 + margin%)
            HDD18 - days with degree 18 by certain temp standard.
            marge for defrost, wind, other uncertain environment conditions
		"""
		for rec in self:
			value = 0.0
			try:
				hdd18 = rec.hdd_value or 0.0
				delta = rec.delta_t or 0.0
				
				# get annual heat consumption safely
				try:
					annual = float(rec.annual_heat_consumption or 0.0)
				
				except Exception:
					annual = 0.0
				
				if hdd18 > 0 and delta:
					value = (annual * delta) / (hdd18 * 24.0)
				else:
					value = 10.0  # your chosen fallback
				
				margin = (rec.margin_percent_kw or 0.0) / 100.0
				value *= (1.0 + margin)
			
			except Exception:
				value = 10.0
			
			rec.design_kw = value
	
	
	@api.depends('usable_area_thermal_zone', 'design_kw')
	def _compute_design_heat_square_m2(self):
		"""
		Compute design heat load per m²:
			design_kw * 1000 / usable_area_thermal_zone
			Always assign a value, even on errors or zero division.
		"""
		for rec in self:
			value = 0.0
			try:
				area = rec.usable_area_thermal_zone or 0.0
				if area > 0.0:
					# use the already-computed design_kw
					value = (rec.design_kw or 0.0) * 1000.0 / area
				else:
					value = 0.0  # or maybe None/False, but 0.0 is safer for Float
			
			except Exception:
				value = 0.0
			
			rec.design_heat_square_m2 = value
	
	
	@api.depends('full_load_hours', 'energy_demand', 'usable_area_thermal_zone')
	def _compute_design_ep_heat_loss_full_load(self):
		for rec in self:
			value = 0.0
			try:
				hours = float(rec.full_load_hours or 0.0)
				if hours > 0.0:
					# If heat_consumption depends on other fields, include them in @api.depends
					annual = float(rec.annual_heat_consumption or 0.0)  # kWh/year
					value = annual / hours  # kW
				else:
					value = 0.0
			except Exception:
				value = 0.0
			rec.design_ep_heat_loss_full_load = value
