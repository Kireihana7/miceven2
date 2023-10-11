# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    # ================ RECEPCIÓN ================ #
    def action_print_nomina_matrix(self):

        return {
            "name": "Boleta pesaje - Recepción",
            "type": "ir.actions.act_window",
            "res_model": "print.matriz.nomina",
            "view_mode": "form",
            "context": {
                "default_payslip_run": self.id,
            },
            "target": "new",
        }

   
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    

    def total_asig (self,lineas):
        lineas_filtradas=lineas.filtered(lambda x:x.appears_on_payslip and x.category_id.name !='Deducción' and x.category_id.code !='COMP')
        return sum(lineas_filtradas.mapped('total'))


    def total_deduc(self,lineas):
        lineas_filtradas=lineas.filtered(lambda x:x.appears_on_payslip and x.category_id.name == 'Deducción')
        return sum(lineas_filtradas.mapped('total'))
    def total_aportem (self,lineas):
        lineas_filtradas=lineas.filtered(lambda x:x.appears_on_payslip and x.category_id.code == 'COMP')
        return sum(lineas_filtradas.mapped('total'))