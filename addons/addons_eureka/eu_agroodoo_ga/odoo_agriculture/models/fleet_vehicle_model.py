# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    farm_equipment = fields.Boolean('Is it a Farm Equipment?')