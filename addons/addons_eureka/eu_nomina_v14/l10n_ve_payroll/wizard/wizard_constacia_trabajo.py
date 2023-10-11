from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
from xlrd import open_workbook
import base64


class ConstanciaTrabajo(models.TransientModel):
    
    _name="constancy.work"

    dirigido = fields.Char(string="Dirigido a")    

    def print_constancia(self):
       

        data={
            'dirigido' : self.dirigido, 
            'docs': self.env['hr.employee'].search([])
        }

        return self.env.ref('l10n_ve_payroll.action_report_constancia_trabajo').report_action(self,data=data)
