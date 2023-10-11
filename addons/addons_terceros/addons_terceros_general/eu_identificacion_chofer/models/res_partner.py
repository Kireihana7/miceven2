# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #@api.depends('vehicle_ids')
    #def _compute_es_chofer_partner(self):
    #    for rec in self:
    #        rec.es_chofer_partner = True if len(rec.vehicle_ids) > 0 else False

    es_chofer_partner = fields.Boolean(
        string='Es Chofer',
        readonly = True,
        #compute="_compute_es_chofer_partner",
        store = True,
    )

    vehicle_ids = fields.One2many(
        'fleet.vehicle',
        'driver_id',
        string='Vehículos Asignados',
        readonly = True,
    )

    