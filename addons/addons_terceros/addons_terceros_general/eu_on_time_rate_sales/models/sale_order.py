# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_entrega_requerida = fields.Boolean(
        related='company_id.fecha_entrega_requerida',
        string='Requiere Fecha de Entrega en las Ventas',
    )