# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    weight_capacity = fields.Float(string="Weight Capacity",tracking=True)
    volume_capacity = fields.Float(string="Volume Capacity",tracking=True)