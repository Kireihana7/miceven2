# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


TODAY=datetime.today()
class PayCompromiseWizard(models.TransientModel):
    _inherit = 'pay.compromise.wizard'

    def create_pay_compromise(self):

        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        rate_today=self.company_id.currency_id.parent_id.rate if self.company_id.currency_id.rate>0 else 1
        if self._context.get('active_model')=='hr.payslip':

            nominas=self.env['hr.payslip'].search([('id','in',active_ids)]).filtered(lambda c: c.state in ["done"] and c.comprometida==False)
            if not nominas:
                raise UserError("No a seleccionado nominas elegibles")
            if not nominas[0].struct_id.rule_ids.filtered(lambda x: x.account_credit ):
                raise UserError("No existe ningun diario establecido para sus reglas basicas, por favor establezcalo")
            account_move_object=self.env['account.move']
            apunte=account_move_object.create({
                    'date':self.para_fecha,
                    'journal_id':self.diario.id,
                    'currency_id': self.company_id.currency_id.parent_id.id,
                    'ref':f"compromiso de pago nominas (ver narración) - {self.para_fecha}"
                })
            nomina_por_pagar_diary=nominas[0].struct_id.rule_ids.filtered(lambda x: x.account_credit )[0].account_credit if nominas else False

            for nom in nominas:
                if apunte.narration:
                    apunte.narration+=f" {nom.number}"
                else:
                    apunte.narration=f"{nom.number}"
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id, 'account_id': nomina_por_pagar_diary.id,'debit':round(nom.total_sum/nom.tax_today,4),'amount_currency':round(nom.total_sum,4)})]})
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id, 'account_id': self.diario.payment_credit_account_id.id,'credit':round(nom.total_sum/nom.tax_today,4),'amount_currency':-1*round(nom.total_sum,4)})]})
                nom.comprometida=True   #no cambie nada a ca porque como tal usaremos esto en el valor de la compañia, si no es asi entonces dividir entre el rate
                nom.bank_journal_id=self.diario
                nom.account_compromise=apunte

            apunte.action_post()
        elif self._context.get('active_model')=='hr.prestaciones.employee.line':
            lineas=self.env['hr.prestaciones.employee.line'].search([('id','in',active_ids)]).filtered(lambda c: c.line_type in ["anticipo"] and c.comprometida==False)
            if not lineas:
                raise UserError("No a seleccionado anticipos elegibles")
            if not self.env.company.journal_for_prestaciones:
                raise UserError("No existe ningun diario establecido para sus anticipos o prestaciones, por favor establezcalo")
            account_move_object=self.env['account.move']
            apunte=account_move_object.create({
                    'date':self.para_fecha,
                    'journal_id':self.diario.id,
                    'currency_id': self.company_id.currency_id.parent_id.id,
                    'ref':f"compromiso de pago anticipos (ver narración) - {self.para_fecha}"
                })
            

            for nom in lineas:
                nomina_por_pagar_diary=self.env.company.asiento_antiguedad_anti_p
                if nom.is_anticipo_intereses:
                    nomina_por_pagar_diary=self.env.company.asiento_interes_anti_paga

                if apunte.narration:
                    apunte.narration+=f" {nom.name}"
                else:
                    apunte.narration=f"{nom.name}"
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id, 'account_id': nomina_por_pagar_diary.id,'debit':round(nom.anticipos_otorga/rate_today,4),'amount_currency':round(nom.anticipos_otorga,4)})]})
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id, 'account_id': self.diario.default_account_id.id,'credit':round(nom.anticipos_otorga/rate_today,4),'amount_currency':-1*round(nom.anticipos_otorga,4)})]})
                if round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4) >0:
                    apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id,'name':'Ajust. por dif. cambiario', 'account_id': nomina_por_pagar_diary.id,'credit':round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4),'amount_currency':-1*round(round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4)*rate_today,4)})]})
                    apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id,'name':'Ajust. por dif. cambiario', 'account_id': self.diario.default_account_id.id,'debit':round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4),'amount_currency':round(round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4)*rate_today,4)})]})
                elif round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4) <0:
                    apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id,'name':'Ajust. por dif. cambiario','account_id': self.diario.default_account_id.id,'credit':round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4),'amount_currency':-1*round(round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4)*rate_today,4)})]})
                    apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id,'currency_id': self.company_id.currency_id.parent_id.id,'name':'Ajust. por dif. cambiario','account_id': nomina_por_pagar_diary.id,'debit':round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4),'amount_currency':round(round(nom.anticipos_otorga_ref-round(nom.anticipos_otorga/rate_today,4),4)*rate_today,4)})]})
                else:
                    pass
                nom.comprometida=True   #aca si dividimos entre rate porque las prestaciones y anticipos estan supuestamente en bolivares
            apunte.action_post()