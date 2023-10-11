# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    third_payment = fields.Boolean(string="Pagar a Tercero")
    autorizado = fields.Many2one('res.partner.autorizados',domain="[('partner_id','=',partner_id)]")
    
    def _prepare_invoice(self, move=False):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res.update({
            'third_payment':self.third_payment,
            'autorizado':self.autorizado.id,
            })
        return res