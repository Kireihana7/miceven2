# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.osv import expression


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # @api.model
    # def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
    #     args = args or []

    #     domain = [
    #         *['|'] * 1,
    #         *map(
    #             lambda field: (field, operator, name),
    #             ['name', 'license_plate']
    #         ),
    #     ] if name else []

    #     return self._search(domain + args, 
    #         limit = limit, 
    #         access_rights_uid = name_get_uid
    #     )