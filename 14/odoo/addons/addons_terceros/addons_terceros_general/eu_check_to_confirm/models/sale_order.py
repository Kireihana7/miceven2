# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.osv import expression

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    modificar_so = fields.Boolean(
        string="Modificar Precio de Venta",
        default=False,
        store=False,compute="_see_price_modified"
        )

    @api.depends('currency_id','user_id','amount_total')
    def _see_price_modified(self):
        for rec in self:
            if rec.env.user.has_group('eu_check_to_confirm.group_modificar_so'):
                rec.modificar_so=True
            else:
                rec.modificar_so=False
    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if self.env.user.has_group('eu_check_to_confirm.group_modificar_so'):
            res.update({'modificar_so': True})
        return res


# class FleetVehicle(models.Model):
#     _inherit = 'fleet.vehicle'

#     @api.model
#     def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
#         args = args or []

#         domain = [
#             *['|'] * 1,
#             *map(
#                 lambda field: (field, operator, name),
#                 ['name', 'license_plate']
#             ),
#         ] if name else []

#         return self._search(expression.AND([domain, args]), 
#             limit = limit, 
#             access_rights_uid = name_get_uid
#         )