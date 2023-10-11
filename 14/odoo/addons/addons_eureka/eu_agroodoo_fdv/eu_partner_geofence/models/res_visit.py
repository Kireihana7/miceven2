# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class ResVisitInherit(models.Model):
    _inherit = 'res.visit'

    partner_geofence = fields.Boolean()

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        res.partner_geofence = res.partner_id.is_geofence
        return res

    def eu_custom_button_visitando_geofence(self):
        pass

    def get_partner_geofence(self, partner_id):
        geofence_location_id = self.env['res.partner'].search([('id', '=', partner_id)]).geofence_location_id
        if geofence_location_id:
            data = {
               "id": geofence_location_id.id,
               "name": geofence_location_id.name,
               "overlay_paths": geofence_location_id.overlay_paths
            }
            return [data]
        return []
    
    @api.onchange('partner_id')
    def onchange_partner(self):
        self.partner_geofence = self.partner_id.is_geofence