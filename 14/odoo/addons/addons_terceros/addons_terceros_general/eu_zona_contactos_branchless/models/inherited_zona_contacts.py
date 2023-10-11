
from odoo import models, fields, api

class InHeritResPartner(models.Model):
    _inherit = 'res.partner'

    partner_zone = fields.Many2one('res.partner.zones', string="Zona")
