
from odoo import models, fields, api,_
from odoo.exceptions import UserError
class BiPayrollWizard(models.TransientModel):
    _name = "bi.payroll.wiz"

    desde = fields.Date('Desde')
    hasta = fields.Date('Hasta')
    tipo_reporte=fields.Selection([('normal','Normal'),('vacation','Vacaciones'),('utility','Utilidades')])
    company_id = fields.Many2one('res.company',string='Compañía',required=True,default=lambda self: self.env.company.id,copy=True)
    payroll_structure_prime=fields.Many2one('hr.payroll.structure',string="Estructura a la izquierda")
    payroll_structure_subprime=fields.Many2one('hr.payroll.structure',string="Estructura a la derecha")
    employee_tags=fields.Many2many('hr.employee.category',string="Categorias empleados")

    def report_print(self):
        if self.tipo_reporte=='normal':
            return self.env.ref('eu_bi_structure_payroll_report.custom_action_report_binominal').report_action(self)
        elif self.tipo_reporte=='vacation':
            return self.env.ref('eu_bi_structure_payroll_report.custom_action_report_vacaciones').report_action(self)
        else:
            return self.env.ref('eu_bi_structure_payroll_report.custom_action_report_utilidades').report_action(self)