# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, _

class EosFeature(models.Model):
    _name = 'eos.feature'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'eos.model']

    name = fields.Char(
        string='Name',
        readonly=True,
        default=lambda self: _('New')
    )

    # Properties:
    shop_prop = fields.Boolean(string='Shop')   
    name_prop = fields.Char(string='Name')            

    # Geometry:
    geometry_type = fields.Selection(
        [
            ('Point', 'Point'),
            ('MultiPoint', 'MultiPoint'),
            ('LineString', 'LineString'),
            ('MultiLineString', 'MultiLineString'),
            ('Polygon', 'Polygon'),
        ],
        string='Action',
        required=True,
    )  

    longitude = fields.Char(string='Longitude')
    latitude = fields.Char(string='Latitude')

    @api.model    
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('eos.feature') or _('New')        
        res = super(EosFeature, self).create(vals)
        return res

    def get_eos_url(self):
        return "https://vt.eos.com/api/data/feature/"

    def action_fetch_from_eos(self):
        KEY =  self.get_key()

        for rec in self: 
            params = {
                "key": rec.name,
                "type": "Feature",
                "properties": {
                    "shop": rec.shop_prop,
                    "name": rec.name_prop,
                },
                "geometry": {
                    "type": rec.geometry_type,
                    "coordinates": [
                        float(rec.longitude),
                        float(rec.latitude),
                    ]
                }
            }

            if not rec.eos_id:
                params.update({
                    "action": "create",
                    "message": "Feature creation",
                })
            else:
                params.update({
                    "message": "Feature modification",
                    "version": rec.version,
                    "action": "modify",
                    "id": rec.eos_id,
                })

            response = requests.post(
                rec.get_eos_url(), 
                headers=rec.get_header(),
                json=params,
            )

            response.raise_for_status()

            data = response.json()

            rec.write({
                "eos_id": data.get("id"),
                "version": rec.version + 1,
            })
    
    def action_delete_from_eos(self):
        for rec in self: 
            params = {
                "key": rec.name,
                "action": "delete",
                "id": rec.eos_id,
                "version": rec.version,
                "type": "Feature",
                "message": "Delete",
                "properties": {
                    "shop": rec.shop_prop,
                    "name": rec.name_prop,
                },
                "geometry": {
                    "type": rec.geometry_type,
                    "coordinates": [
                        float(rec.longitude),
                        float(rec.latitude),
                    ]
                }
            }

            response = requests.post(
                rec.get_eos_url(), 
                headers=rec.get_header(),
                json=params,
            )

            response.raise_for_status()

        self.write({
            "eos_id": None,
            "version": 0,
        })