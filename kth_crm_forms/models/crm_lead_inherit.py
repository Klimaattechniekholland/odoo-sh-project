# -*- coding: utf-8 -*-
"""
Extension of the crm.lead model to include intake questionnaire fields.

The additional fields capture customer and project details collected via
the intake portal form.  These fields support both English and Dutch
translations and can be filled from the portal or directly in the
backend.
"""

from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # Basic contact information (mandatory on portal)
    full_name = fields.Char(
        string="Full Name / Volledige naam",
        help="Customer’s full name (required)",
        copy=False,
    )
    email_from = fields.Char(
        string="Email / E‑mail",
        help="Primary email address", copy=False
    )
    phone = fields.Char(
        string="Telephone / Mobile / Telefoon",
        help="Primary phone number", copy=False
    )
    address = fields.Char(
        string="Address / Adres",
        help="Street and house number", copy=False
    )
    zip_code = fields.Char(
        string="Zip / Postcode",
        help="Postal code", copy=False
    )
    house_number = fields.Char(
        string="House Number / Huisnummer",
        help="House number (optional)", copy=False
    )

    # Heat Pump (Warmtepomp) section
    type_system = fields.Selection([
        ('hybrid', 'Hybride'),
        ('all_electric_ready', 'All Electric Ready'),
        ('all_electric', 'All Electric')
    ], string="Type Systeem / Type System")
    brand = fields.Selection([
        ('vaillant', 'Vaillant'),
        ('viessmann', 'Viessmann'),
        ('weheat', 'WeHeat'),
        ('remeha', 'Remeha')
    ], string="Merk / Brand")
    floor_surface = fields.Integer(
        string="Floor Surface (m²) / Vloeroppervlak",
        help="Total heated floor surface in square metres"
    )
    type_heating = fields.Selection([
        ('floor_radiators', 'Vloerverwarming + Radiatoren'),
        ('floor_only', 'Alleen Vloerverwarming'),
        ('radiators_only', 'Alleen Radiatoren')
    ], string="Type Heating / Type verwarming")
    gas_consumption = fields.Integer(
        string="Gas Consumption / Gasverbruik (per jaar)",
        help="Annual gas consumption in cubic metres"
    )
    energy_label = fields.Selection([
        ('a++++', 'A++++'), ('a+++', 'A+++'), ('a++', 'A++'),
        ('a+', 'A+'), ('b', 'B'), ('c', 'C'), ('d', 'D'),
        ('e', 'E'), ('f', 'F'), ('g', 'G')
    ], string="Energy Label / Energielabel")
    year_built = fields.Integer(
        string="Year Built / Bouwjaar",
        help="Year the house was built"
    )
    ventilation = fields.Selection([
        ('a', 'Type A'),
        ('b', 'Type B'),
        ('c', 'Type C'),
        ('d', 'Type D (WtW)')
    ], string="Ventilation / Ventilatie")
    members = fields.Integer(
        string="Members / Gezinsleden",
        help="Number of household members"
    )
    average_usage = fields.Selection([
        ('economic', 'Economisch'),
        ('standard', 'Standaard'),
        ('luxury', 'Luxe')
    ], string="Average Usage / Gemiddeld verbruik")
    extra_notes = fields.Text(
        string="Extra Notes / Extra notities",
        help="Any additional remarks or requirements"
    )

    # Airco section
    airco_model = fields.Char(
        string="Airco Model / Airco model",
        help="Model or type of air conditioning system"
    )
    airco_capacity = fields.Integer(
        string="Airco Capacity (kW) / Airco capaciteit (kW)",
        help="Required cooling capacity in kilowatts"
    )

    # Service contracts section
    service_contract_type = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string="Service Contract / Servicecontract")

    # Call‑out section
    callout_issue = fields.Text(
        string="Call‑Out Issue / Storingsomschrijving",
        help="Description of the problem for a service call‑out"
    )

    def action_open_intake_portal(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/intake',
            'target': 'new',
        }