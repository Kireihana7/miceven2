# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    fecha_entrega_requerida = fields.Boolean(
        string='Requiere Fecha de Entrega en las Ventas',
    )