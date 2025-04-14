from odoo import models, api

class CrmPipelineKlimaatWizard(models.TransientModel):
    _name = 'crm.pipeline.klimaat.wizard'
    _description = 'CRM Pipeline Generator Wizard'

    @api.model
    def generate_pipeline(self):
        stages = ['Nieuw', 'Intake', 'Offerte', 'Goedgekeurd', 'Installatie', 'Afgerond']
        team_id = self.env['crm.team'].search([], limit=1).id

        for stage_name in stages:
            self.env['crm.stage'].create({
                'name': stage_name,
                'team_id': team_id,
                'sequence': stages.index(stage_name) * 10,
            })

        return {'type': 'ir.actions.act_window_close'}
    