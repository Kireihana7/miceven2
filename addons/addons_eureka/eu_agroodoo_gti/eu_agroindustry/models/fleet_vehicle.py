# -*- coding: utf-8 -*-

from odoo import models, fields, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_type_property    = fields.Selection([
        ('propio', 'Propio'),
        ('tercero', 'De tercero'),
        ], string="¿Es un vehículo de Tercero?", copy=False, tracking=True, default='propio',)
    vehicle_owner   = fields.Many2one('res.partner',string="Propietario del Vehículo")
    with_trailer    = fields.Boolean(string="¿Tiene Remolque?")
    plate_trailer   = fields.Char(string="Placa del Remolque")
    
    driver_id = fields.Many2one('res.partner', 'Driver', tracking=True, help='Driver of the vehicle', copy=False,domain=[('company_type','=','person')])