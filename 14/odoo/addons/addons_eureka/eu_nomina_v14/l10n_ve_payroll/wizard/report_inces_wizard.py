# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
TODAY = date.today()
def current_electables():
        mes=TODAY.month
        array=[('1','Primer Trimestre')]
        # if mes >3:
        array.append(('2','Segundo Trimestre'))
        # if mes>6:
        array.append(('3','Tercer Trimestre'))
        # if mes>9:
        array.append(('4','Cuarto Trimestre'))
        return array

class IncesReportWizard(models.TransientModel):
    _name = 'report.inces.wizard'
    _description = 'Reporte trimestral de Inces'




    @api.model
    def _default_fecha_inicio(self):
        
        if TODAY.day <=15:
            current_date = date(TODAY.year,TODAY.month,1)
        else:
            current_date = date(TODAY.year,TODAY.month,16)
        return current_date
    

    para_fecha = fields.Date("Fecha Inicio", default=TODAY)
    trimestre = fields.Selection(current_electables(),string="Para que trimestre del año")
    autoriza_retencion = fields.Boolean(string="Solo aquellos que autorizan retención",default=True)
    employee_tags=fields.Many2many('hr.employee.category',string="Categorias empleados")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,invisible=True)

    
        
    def print_report(self):
        
        
        return self.env.ref('l10n_ve_payroll.action_report_inces_trimestral').report_action(self)
        

    def print_report2(self):
        
        
        return self.env.ref('l10n_ve_payroll.action_report_inces_trimestral2').report_action(self)
# class ParticularReport(models.AbstractModel):
#     _name = 'report.l10n_ve_payroll.report_acum_rel_nomina_var'

#     def _get_report_values(self, docids, data=None):
#         # get the report action back as we will need its data
        
#         # return a custom rendering context
#         return {
#             'doc_ids':data.get("doc_ids"),
#             'doc_model': data.get("doc_model"),
#             'docs':self.env['hr.employee'].search([('id','in',data.get("doc_ids"))]),
#             'datas':data

#         }