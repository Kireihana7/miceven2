# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    commission_id = fields.Many2one('sale.commission',string="Comisión Vinculada",readonly=True)
    commission_id_line = fields.Many2one('sale.commission.line',string="Línea de Comisión Vinculada",readonly=True)
    commission_id_payment = fields.Many2one('sale.commission.payment',string="Pago de Comisión",readonly=True)