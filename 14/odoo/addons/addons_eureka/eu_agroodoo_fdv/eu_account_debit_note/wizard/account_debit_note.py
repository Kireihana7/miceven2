# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    percentage = fields.Float("Porcentaje", default=100)
    use_product_service = fields.Boolean(string="Usar Servicio",default=False)
    product_id = fields.Many2one('product.product',string="Servicio a utilizar",domain=[('type','=','service')],default=lambda self: self.env.company.product_nd_id.id)
    tipo_monto = fields.Selection([ 
    ('amount_untaxed', 'Base imponible'), 
    ('amount_total', 'Monto total'), 
    ], default="amount_untaxed",
    string='Tipo de Monto',)

    def create_debit(self):
        res = super().create_debit()
        move_id = self.env['account.move'].browse(res.get('res_id'))
        if self.copy_lines and not self.use_product_service and move_id:
            for line in move_id.filtered(lambda m: m.state == "draft").invoice_line_ids:
                line.with_context({'check_move_validity':False}).price_unit = (self.percentage / 100) * line.price_unit
                line.with_context({'check_move_validity':False})._get_computed_taxes()
            move_id.with_context({'check_move_validity':False}).write({'apply_manual_currency_exchange':True})
            move_id.with_context({'check_move_validity':False})._onchange_partner_id()
            move_id.with_context({'check_move_validity':False})._onchange_currency()
        if not self.copy_lines and self.use_product_service and move_id:
            for invoice in move_id:
                monto_total_company = invoice.debit_origin_id.amount_total if self.tipo_monto == 'amount_total' else invoice.debit_origin_id.amount_untaxed
                invoice.invoice_line_ids.unlink()
                apunte = {
                    'account_id': self.product_id.categ_id.property_account_income_categ_id.id if invoice.move_type in ('out_invoice','out_refund') else self.product_id.categ_id.property_account_expense_categ_id.id,
                    'company_id': invoice.company_id.id,
                    'currency_id': invoice.currency_id.id,
                    'date_maturity': False,
                    'date': invoice.date,
                    'partner_id': invoice.partner_id.id,
                    'move_id': invoice.id,
                    'name': self.product_id.display_name,
                    'journal_id': invoice.journal_id.id,
                    'quantity':1,
                    'product_id':self.product_id.id,
                    'price_unit':(self.percentage / 100) * monto_total_company,
                }
                move_line_obj = self.env['account.move.line']
                move_line_obj.with_context(check_move_validity=False).create(apunte)
        return res
