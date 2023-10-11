# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'


    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi'),
        ('horas', 'horas'),
        ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)