from odoo.exceptions import UserError, ValidationError
from odoo import models, fields,api
from odoo.osv import expression


class ResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"


    boss_rrhh=fields.Many2one('hr.employee',string='Jefe Recursos humanos')
    lawyer_ref=fields.Many2one('hr.employee',string='Abogado redactor')
    num_ipsa=fields.Char(string='IPSA. Nº ')
    days_alert_contract=fields.Integer('Diás de alerta vencimiento contrato')

    sent_txt_to_folder=fields.Boolean("Enviar txts a la carpeta",related='company_id.sent_txt_to_folder',readonly=False)

    @api.onchange('sent_txt_to_folder')
    def _onchange_sent_txt_to_folder(self):
        
        if self.company_id.sent_txt_to_folder != self.sent_txt_to_folder:
            self.company_id.sent_txt_to_folder = self.sent_txt_to_folder


   
        