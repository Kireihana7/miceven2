
from odoo import models, fields, api

class InHeritResPartner(models.Model):
    _inherit = 'res.partner'

    partner_zone = fields.Many2one('res.partner.zones', string="Zona")

    
    # city_id = fields.Many2one('res.country.state.city', string="Zona Ciudad")