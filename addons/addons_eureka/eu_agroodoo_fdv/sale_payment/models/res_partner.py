# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, default_fields):
        rec = super(ResPartner, self).default_get(default_fields)
        rec.update({
            'user_id': self.env.uid,
        })
        return rec