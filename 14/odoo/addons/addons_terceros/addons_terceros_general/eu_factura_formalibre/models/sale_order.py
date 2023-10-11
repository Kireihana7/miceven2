# -*- coding: utf-8 -*-
import math
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    direccion_completa = fields.Char(
        compute = '_compute_direccion_completa',
        string='Filed Label',
    )

    def _compute_direccion_completa(self):
        for rec in self:
            rec.direccion_completa = " ".join([
                *[x or "" for x in [rec.partner_id.street, rec.partner_id.street2]],
                *[x.name if x else "" for x in [
                    rec.partner_id.city_id, 
                    rec.partner_id.state_id, 
                    rec.partner_id.country_id
                ]]
            ])