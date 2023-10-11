# -*- coding: utf-8 -*-

from odoo import api,fields,models,_

class AccountPaymentIgtf(models.TransientModel):
    _name="account.payment.igtf"
    _description = "IGTF de Pago"

    payment_id = fields.Many2one('account.payment',string="Pago Vinculado",readonly=True,required=True)
    journal_id = fields.Many2one('account.journal',string="Diario en el que se Realizó el IGTF",domain="[('type','in',('cash','bank'))]")
    currency_id = fields.Many2one('res.currency',string="Moneda",readonly=False,required=True)
    amount = fields.Float(string="Monto",readonly=True)
    rate = fields.Float(string="Tasa",readonly=True)
    memo = fields.Char(string="Detalles del Pago")

    def action_create_igtf(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Registro de IGTF'),
            'res_model': len(active_ids) == 1 and 'account.payment.igtf' or 'account.payment.igtf',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_withholding_itf.view_account_payment_igtf_form').id or self.env.ref('eu_withholding_itf.view_account_payment_igtf_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        for rec in self:
            rec.currency_id = rec.journal_id.currency_id.id if rec.journal_id.currency_id else self.env.company.currency_id.id

    def register_payment(self):
        for rec in self:
            if rec.payment_id:
                vals = {
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id':rec.payment_id.partner_id.id,
                    'destination_account_id': rec.payment_id.journal_id.igtf_account.id,
                    'company_id':rec.payment_id.company_id.id,
                    'amount':rec.amount if rec.currency_id == rec.payment_id.currency_id else rec.amount * rec.rate,
                    'ref':rec.memo,
                    'journal_id':rec.journal_id.id,
                    'currency_id':rec.currency_id.id,
                    'manual_currency_exchange_rate':rec.rate,
                    'is_igtf_payment': True,
                }
                payment =  self.env['account.payment'].sudo().create(vals)
                rec.payment_id.igtf_cliente = payment.id

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPaymentIgtf, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Chequea que venga desde el pago
        if not active_ids or active_model != 'account.payment':
            return rec

        payment_id = self.env['account.payment'].browse(active_ids)

        # Revisa que exista un resultado en la busqueda, para no permitir crear un IGTF con el pago cancelado, o sin los campos
        if not payment_id:
            raise UserError(_("Debe tener un Pago para poder crear el IGTF"))
        # Actualiza los campos para la vista
        rec.update({
            'payment_id': payment_id[0].id,
            'journal_id': payment_id[0].journal_id.id,
            'rate': payment_id[0].manual_currency_exchange_rate,
            'amount':(payment_id[0].amount * payment_id[0].journal_id.igtf_percent) / 100,
        })
        return rec