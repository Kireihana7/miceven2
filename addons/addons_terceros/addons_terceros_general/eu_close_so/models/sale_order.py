# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_cerrada = fields.Boolean(string="SO Cerrada")    

    def cerrar_so(self):
        for rec in self:
            if not rec.so_cerrada and len(rec.order_line.filtered(lambda x: x.qty_delivered != x.qty_invoiced))> 0:
                raise UserError('No puedes cerrar una SO que no ha sido facturada completamente')
            else:
                rec.so_cerrada = True
                rec.invoice_status = 'invoiced'

