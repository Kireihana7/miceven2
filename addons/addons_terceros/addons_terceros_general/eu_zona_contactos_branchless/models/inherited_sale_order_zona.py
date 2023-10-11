
from odoo import models, fields, api

class InHeritResPartner(models.Model):
    _inherit = 'sale.order'


    @api.onchange('partner_id')
    def _onchange_partner_zone(self):
        for rec in self:
            rec.partner_zone = rec.partner_id.partner_zone.id 

    partner_zone = fields.Many2one('res.partner.zones', string="Zona")

class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_zone = fields.Many2one(related="partner_id.partner_zone", string="Zona", store=True) 
    
