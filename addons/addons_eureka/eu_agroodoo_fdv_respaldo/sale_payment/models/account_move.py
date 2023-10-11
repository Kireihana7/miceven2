# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order','Venta Vinculada')
    sale_id_status = fields.Selection(related="sale_id.state",string="Estatus de la SO")

    def show_payment_invoice(self):
        if self.sale_id:
            self.ensure_one()
            res = self.env.ref('account.action_account_payments')
            res = res.read()[0]
            res['domain'] = str([('sale_id', '=', self.sale_id.id)])
            return res
        else:
            raise UserError('La factura no tiene una venta asociada')

    payment_count_inv = fields.Integer("Pago", compute='_compute_payment_count_inv')

    @api.depends('sale_id')
    def _compute_payment_count_inv(self):
        for payment in self:
            payment.payment_count_inv = 0 
            if payment.sale_id:
                payment.payment_count_inv = self.env['account.payment'].sudo().search_count([('sale_id', '=', payment.sale_id.id),('company_id', '=', payment.company_id.id)])