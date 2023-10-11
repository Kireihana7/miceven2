# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetTripRoute(models.AbstractModel):
    _name = "fleet.trip.route"
    _description = "Ruta de viajes"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    origin_branch_id = fields.Many2one("res.branch", "Sucursal de origen", tracking=True)
    origin_city_id = fields.Many2one("res.country.state.city", "Ciudad de origen", tracking=True)
    destination_branch_id = fields.Many2one("res.branch", "Sucursal destino", tracking=True)
    destination_city_id = fields.Many2one("res.country.state.city", "Ciudad destino", tracking=True)
    route_type = fields.Selection([
        ("city_city", "Ciudad-ciudad"),
        ("branch_branch", "Sucursal-sucursal"),
        ("city_branch", "Ciudad-sucursal"),
        ("branch_city", "Sucursal-ciudad"),
    ], "Tipo de ruta", tracking=True)