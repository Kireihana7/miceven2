# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    third_payment = fields.Boolean(string="Pagar a Tercero")
    autorizado = fields.Many2one('res.partner.autorizados',domain="[('partner_id','=',partner_id)]")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Centro de Costo')
    fatura_rapida = fields.Many2one('account.move',string="Factura Rápida")

    def create_invoice(self,currency_id,partner_id,journal_id,tipo_pago):
        invoice_id = self.env["account.move"].create({
            "partner_id": partner_id.id,
            "partner_shipping_id": partner_id.id,
            "journal_id": self.env['account.move']
                .with_context(default_move_type=tipo_pago )
                ._get_default_journal()
                .id,
            "currency_id": currency_id.id,
            "invoice_date": date.today(),
            "company_id": self.env.company,
            "move_type": tipo_pago,
            "invoice_payment_term_id": False,
            'apply_manual_currency_exchange':self.apply_manual_currency_exchange,
            'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
        })

        return invoice_id

    def create_lineas_vals(self, product_id,invoice_id,monto):
        return {
            'name': product_id.display_name,
            'product_id': product_id.id,
            'price_unit': monto,
            'move_id': invoice_id.id,
            'quantity':1,
            'product_uom_id':product_id.uom_id.id,
            "account_id": product_id.categ_id.property_account_income_categ_id.id,
        }

    def facturar(self):
        for rec in self:
            journal_id = rec.journal_id
            monto = rec.amount
            partner_id = rec.partner_id
            product_id = rec.company_id.product_payment_id
            currency_id = journal_id.currency_id if journal_id.currency_id else self.env.company.currency_id
            tipo_pago =  False
            if rec.partner_type == 'supplier' and rec.payment_type == 'outbound':
                tipo_pago = 'in_invoice'
            if rec.partner_type == 'supplier' and rec.payment_type == 'inbound':
                tipo_pago = 'in_refund'
            if rec.partner_type == 'customer' and rec.payment_type == 'inbound':
                tipo_pago = 'out_invoice'
            if rec.partner_type == 'customer' and rec.payment_type == 'outbound':
                tipo_pago = 'out_refund'
            if tipo_pago == False:
                raise UserError('El tipo de Pago no es válido')
            if not product_id:
                raise UserError('Debe configurar el Producto a usar en la Compañía')
            invoice_id = rec.create_invoice(currency_id,partner_id,journal_id,tipo_pago)

            vals = rec.create_lineas_vals(product_id,invoice_id,monto)

            invoice_id.invoice_line_ids.with_context(check_move_validity=False).create(vals)
            invoice_id.with_context(check_move_validity=False)._onchange_partner_id()
            #invoice_id.invoice_line_ids._onchange_product_id()

            #for i, line in enumerate(invoice_id.invoice_line_ids):
            #    line.price_unit = self[i].amount * rate

            invoice_id._onchange_manual_currency_rate()
            invoice_id.invoice_line_ids._onchange_mark_recompute_taxes()
            invoice_id.invoice_line_ids._onchange_price_subtotal()
            invoice_id._onchange_invoice_line_ids()

            rec.write({"fatura_rapida": invoice_id.id})

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    third_payment = fields.Boolean(string="Pagar a Tercero")
    autorizado = fields.Many2one('res.partner.autorizados',domain="[('partner_id','=',partner_id)]")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Centro de Costo')
    
    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'third_payment':self.third_payment,
            'autorizado':self.autorizado.id,
            'analytic_account_id':self.analytic_account_id.id,
        })
        return result


    @api.model
    def default_get(self, fields):
        result = super(AccountPaymentRegister, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'third_payment':move_id[0].third_payment,
            'autorizado':move_id[0].autorizado.id,
            })
        return result