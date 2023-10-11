# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    def show_quality_mrp(self):
        self.ensure_one()
        res = self.env.ref('quality_control.quality_check_action_main')
        res = res.read()[0]
        res['domain'] = str([('production_id', '=', self.id),('company_id', '=', self.env.company.id)])
        return res

    quality_count = fields.Integer("Calidad", compute='_compute_quality_count')

    def _compute_quality_count(self):
        for production in self:
            production.quality_count = self.env['quality.check'].search_count([('production_id', '=', production.id),('company_id', '=', self.env.company.id)])
    