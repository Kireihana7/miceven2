# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    percentage = fields.Float("Porcentaje", default=100)
    use_product_service = fields.Boolean(string="Usar Servicio",default=False)
    product_id = fields.Many2one('product.product',string="Servicio a utilizar",domain=[('type','=','service')])
    tipo_monto = fields.Selection([ 
    ('amount_untaxed', 'Base imponible'), 
    ('amount_total', 'Monto total'), 
    ], default="amount_untaxed",
    string='Tipo de Monto',)


    def reverse_moves(self):
        res = super().reverse_moves()

        if self.refund_method == "refund":
            if not self.use_product_service:
                for line in self.new_move_ids.filtered(lambda m: m.state == "draft").invoice_line_ids:
                    line.with_context({'check_move_validity':False}).price_unit = (self.percentage / 100) * line.price_unit
                    line.with_context({'check_move_validity':False})._get_computed_taxes()
                self.new_move_ids.with_context({'check_move_validity':False}).write({'apply_manual_currency_exchange':True})
                self.new_move_ids.with_context({'check_move_validity':False})._onchange_partner_id()
                self.new_move_ids.with_context({'check_move_validity':False})._onchange_currency()
            if self.use_product_service:
                for invoice in self.new_move_ids:
                    monto_total_company = abs(invoice.amount_total if self.tipo_monto == 'amount_total' else invoice.amount_untaxed)
                    invoice.invoice_line_ids.unlink()
                    invoice.invoice_line_ids.with_context(check_move_validity=False).create(self.create_lineas_vals(self.product_id,invoice,(self.percentage / 100) * monto_total_company))
                    invoice.with_context(check_move_validity=False)._onchange_partner_id()
        return res

    def create_lineas_vals(self, product_id,invoice_id,monto):
        return {
            'name': product_id.display_name,
            'product_id': product_id.id,
            'price_unit': abs(monto),
            'move_id': invoice_id.id,
            'quantity':1,
            'product_uom_id':product_id.uom_id.id,
            "account_id": product_id.categ_id.property_account_income_categ_id.id if invoice_id.move_type =='out_refund' else product_id.categ_id.property_account_expense_categ_id.id,
        }