# hooks.py
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    """Hook to clean up crm.stage and align with predefined ones."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    predefined_names = {
        'Nieuwe Lead', 'Intake', 'Voorlopige Offerte', 'Schouw',
        'Definitieve Offerte', 'Opdracht Bevestigd', 'Insta. Datum',
        'Installatie', 'Oplevering', 'Facturatie'
    }

    # Get all existing CRM stages
    existing_stages = env['crm.stage'].search([])
    names_to_keep = set(predefined_names)
    default_stage = existing_stages.filtered(lambda s: s.name.lower() in ['new', 'nieuw'])

    # Rename 'New' to 'Nieuwe Lead' if 'Nieuwe Lead' not already present
    if 'Nieuwe Lead' not in existing_stages.mapped('name'):
        for stage in default_stage:
            stage.name = 'Nieuwe Lead'

    # Delete or fold stages not in our predefined list
    for stage in existing_stages:
        if stage.name not in names_to_keep:
            if stage.id and not stage.fold:
                stage.fold = True
            if stage.name.lower() not in ['new', 'nieuw']:
                stage.unlink()
