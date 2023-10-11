# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self):
        res =  super(MrpProduction, self).action_confirm()
        for record in self:
            record.action_variances_postings()
            record.action_economical_closure()
            record.closure_state = 'True'
        return res

    