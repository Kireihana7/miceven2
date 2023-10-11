# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def create_invoices(self):
        super(SaleAdvancePaymentInv, self).create_invoices()
        # raise UserError(_('Método "create_invoices"'))