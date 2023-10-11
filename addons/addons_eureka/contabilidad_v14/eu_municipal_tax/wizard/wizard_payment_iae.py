# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountPayIae(models.Model):
    _name = "account.iae.pay"
    _order = 'payment_date desc'
    _description = "Pagar Declaracion Mensual Ingresos IAE"
    
    name = fields.Char(readonly=True, copy=False, default="Pago Declaración Mensual de Ingresos")
    account_id = fields.Many2one('account.account',  string='Cuenta Contable', required=True, help="Cuenta Contable respectiva")
    amount = fields.Monetary(string='Monto a Pagar', required=True,readonly=True,help="Monto a pagar al municipio por declaración de ingresos")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Fecha de Pago', default=fields.Date.context_today, required=True, copy=False,help="Fecha en la que se realizó el pago")
    communication = fields.Char(string='Circular',help="Descripción opcional del pago")
    journal_id = fields.Many2one('account.journal', string='Diario de Pago', required=True, domain=[('type', 'in', ('bank', 'cash'))],help="Diario en la cual saldra el Pago")
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    tax_municipal = fields.Many2one('tax.municipal',string="Declaración",required=True,readonly=True,help="Declaracion Mensual de ingresos")
    move_id = fields.Many2one('account.move',string="Asiento Contable del Pago",readonly=True,help="Asiento contable que genera el pago al Validar")
    def action_pays_iae(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Pago de Declaracion Mensual de Ingresos '),
            'res_model': len(active_ids) == 1 and 'account.iae.pay' or 'account.iae.pay',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_municipal_tax.view_pay_iae_view_form').id or self.env.ref('eu_municipal_tax.view_pay_iae_view_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayIae, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde la Orden
        if not active_ids or active_model != 'tax.municipal':
            return rec

        tax_municipal = self.env['tax.municipal'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear una carga manual sin consolidado
        if not tax_municipal:
            raise UserError(_("Para crear un Pago de Declaracion Mensual de Ingresos, debe hacerlo desde la Declaracion Directamente"))
        # Actualiza los campos para la vista
        rec.update({
            'tax_municipal': tax_municipal[0].id,
            'amount': tax_municipal[0].total_iae,
        })
        return rec
   
    def pay_tax_municipal(self):
        # TO DO Multi Currency
        line_ids = []
        self.name=self.env['ir.sequence'].next_by_code('account.payment.iae.out_invoice')
        for pay in self:
            move_dict = {
                    'ref': pay.name,
                    'narration': pay.communication,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'muni_declaration': self.tax_municipal.id,
                }
            
            credit_account_id = pay.journal_id.payment_credit_account_id.id
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Pago del IAE Declaración Mensual',
                    'account_id': credit_account_id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': False,
                    'credit': pay.amount,
                })
                line_ids.append(credit_line)
            if pay.account_id:
                debit_line = (0, 0, {
                    'name': 'Pago del IAE Declaración Mensual',
                    'account_id': pay.account_id.id,
                    'journal_id': pay.journal_id.id,
                    'date': pay.payment_date,
                    'debit': pay.amount,
                    'credit': False,
                })
                line_ids.append(debit_line)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.post()
            self.move_id=move.id
            self.tax_municipal.pay_move_id = move.id
            list_line=[]
            if move:
                for wh in pay.tax_municipal.invoice_line:
                    #raise UserError(('%s') %(wh.invoice_id.status_account))
                    if wh.invoice_id.status_account == 'declared':
                        list_line.append(wh.invoice_id.id)
            #raise UserError(('%s') %(list_line)) chivo expiatorio
            pay.tax_municipal.write({'state':'done'})
            self.env['account.move'].search([('id','in',list_line)]).write({'status_account':'done'})
        return True