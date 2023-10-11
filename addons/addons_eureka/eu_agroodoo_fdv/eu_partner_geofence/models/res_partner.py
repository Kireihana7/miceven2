# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import date

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    is_geofence = fields.Boolean('Es Geocerca')
    geofence_location_id = fields.Many2one('hr.attendance.geofence', string='Geocerca', domain="[('partner_id', '=', id)]")

    def get_is_geofence(self, partner_id):
        partner_obj = self.browse(partner_id)
        if partner_obj:
            return partner_obj.is_geofence
        
    def get_geofence_location_id(self, partner_id):
        partner_obj = self.browse(partner_id)
        if partner_obj:
            return partner_obj.geofence_location_id
        
    def set_current_position(self, partner_id, lat, long):
        partner_obj = self.browse(partner_id)
        if partner_obj:
            partner_obj.date_localization = date.today()
            partner_obj.partner_latitude = lat
            partner_obj.partner_longitude = long
        
    def eu_custom_button_auto_geofence(self):
        pass

    def eu_custom_button_geolocalize(self):
        pass
