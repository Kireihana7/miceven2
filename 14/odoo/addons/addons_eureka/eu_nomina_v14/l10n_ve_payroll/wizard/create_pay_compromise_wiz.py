# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import UserError
from datetime import date,datetime
from calendar import monthrange
TODAY = date.today()


class PayCompromiseWizard(models.TransientModel):
    _name = 'pay.compromise.wizard'
    _description = 'crea asientos para diario de pago'

    para_fecha = fields.Date("Fecha Inicio", default=TODAY)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,invisible=True)
    diario =fields.Many2one('account.journal', string="diario del asiento",required=True)
    
        
    
    def create_pay_compromise(self):

        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        if self._context.get('active_model')=='hr.payslip':

            nominas=self.env['hr.payslip'].search([('id','in',active_ids)]).filtered(lambda c: c.state in ["done"] and (c.comprometida==False or c.account_compromise==False))
            if not nominas:
                raise UserError("No a seleccionado nominas elegibles")
            if not nominas[0].struct_id.rule_ids.filtered(lambda x: x.account_credit ):
                raise UserError("No existe ningun diario establecido para sus reglas basicas, por favor establezcalo")
            account_move_object=self.env['account.move']
            apunte=account_move_object.create({
                    'date':self.para_fecha,
                    'journal_id':self.diario.id,
                    'ref':f"compromiso de pago nominas (ver narración) - {self.para_fecha}"
                })
            nomina_por_pagar_diary=nominas[0].struct_id.rule_ids.filtered(lambda x: x.account_credit )[0].account_credit if nominas else False

            for nom in nominas:
                if apunte.narration:
                    apunte.narration+=f" {nom.number}"
                else:
                    apunte.narration=f"{nom.number}"
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id, 'account_id': nomina_por_pagar_diary.id,'debit':nom.total_sum})]})
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id, 'account_id': self.diario.payment_credit_account_id.id,'credit':nom.total_sum})]})
                nom.comprometida=True
                nom.bank_journal_id=self.diario
                nom.account_compromise=apunte
            apunte.action_post()
        elif self._context.get('active_model')=='hr.prestaciones.employee.line':
            lineas=self.env['hr.prestaciones.employee.line'].search([('id','in',active_ids)]).filtered(lambda c: c.line_type in ["anticipo"] and c.comprometida==False )
            if not lineas:
                raise UserError("No a seleccionado anticipos elegibles")
            if not self.env.company.journal_for_prestaciones:
                raise UserError("No existe ningun diario establecido para sus anticipos o prestaciones, por favor establezcalo")
            account_move_object=self.env['account.move']
            apunte=account_move_object.create({
                    'date':self.para_fecha,
                    'journal_id':self.diario.id,
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
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id, 'account_id': nomina_por_pagar_diary.id,'debit':nom.anticipos_otorga})]})
                apunte.write({'line_ids': [(0, 0, {'move_id': apunte.id, 'account_id': self.diario.default_account_id.id,'credit':nom.anticipos_otorga})]})
                nom.comprometida=True
            apunte.action_post()
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': title,
        #         'message': message,
        #         'sticky': False,
        #     }
        # }
