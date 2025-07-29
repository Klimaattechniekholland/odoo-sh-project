# -*- coding: utf-8 -*-
"""
HTTP controllers for the intake form exposed on the customer portal.

This controller renders the intake form, validates user input, and
creates a CRM lead with the captured data.  It only accepts
authenticated users (portal) to ensure submissions are associated
with an existing partner.
"""

import re
from odoo import http, _
from odoo.http import request


class PortalIntakeController(http.Controller):
    """Controller for displaying and handling the intake form."""

    @http.route(['/my/intake'], type='http', auth='user', website=True)
    def display_form(self, **kwargs):
        """Render the intake form.

        The form includes multiple tabs for different service types and a
        language toggle.  Errors from a previous submission are passed
        through kwargs to display them at the top of the form.
        """
        values = {
            'errors': kwargs.get('errors'),
            'post': kwargs.get('post'),
        }
        return request.render('kth_crm_forms.portal_intake_form', values)

    @http.route(['/my/intake/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_form(self, **post):
        """Validate and process the intake form submission.

        This method performs basic validation on the mandatory fields
        (full name, email, phone, address) and checks for forbidden
        characters.  If the validation passes, a CRM lead is created
        with the additional intake fields and assigned to the Intake
        stage if it exists.
        """
        errors = []
        # Retrieve and trim values
        name = (post.get('full_name') or '').strip()
        email = (post.get('email_from') or '').strip()
        phone = (post.get('phone') or '').strip()
        address = (post.get('address') or '').strip()

        # Validate mandatory fields
        if not name or not email or not phone or not address:
            errors.append(_('All mandatory fields are required.'))

        # Disallow certain special characters in name and address
        if re.search(r"[#$@!]", name) or re.search(r"[#$@!]", address):
            errors.append(_('Name and address cannot contain special characters (# $ @ !).'))

        # Basic email validation
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors.append(_('Invalid email format.'))

        # Dutch phone number validation: accepts +316XXXXXXXX, 06XXXXXXXX
        if phone and not re.match(r"^(?:\+31|0)6\d{8}$", phone):
            errors.append(_('Invalid Dutch phone number format.'))

        if errors:
            # Pass the posted data back to the form so the user doesn’t lose input
            return self.display_form(errors=errors, post=post)

        # Create a new CRM lead with the submitted values
        intake_stage = request.env['crm.stage'].sudo().search([('name', '=', 'Intake')], limit=1)
        lead_vals = {
            'full_name': name,
            'email_from': email,
            'phone': phone,
            'address': address,
            'zip_code': post.get('zip_code'),
            'house_number': post.get('house_number'),
            'type_system': post.get('type_system'),
            'brand': post.get('brand'),
            'floor_surface': post.get('floor_surface'),
            'type_heating': post.get('type_heating'),
            'gas_consumption': post.get('gas_consumption'),
            'energy_label': post.get('energy_label'),
            'year_built': post.get('year_built'),
            'ventilation': post.get('ventilation'),
            'members': post.get('members'),
            'average_usage': post.get('average_usage'),
            'extra_notes': post.get('extra_notes'),
            # Additional sections
            'airco_model': post.get('airco_model'),
            'airco_capacity': post.get('airco_capacity'),
            'service_contract_type': post.get('service_contract_type'),
            'callout_issue': post.get('callout_issue'),
            # Set stage if found
            'stage_id': intake_stage.id if intake_stage else False,
            # Give the lead a meaningful name
            'name': _('Intake - %s') % name,
        }
        request.env['crm.lead'].sudo().create(lead_vals)

        return request.render('kth_crm_forms.portal_intake_success')