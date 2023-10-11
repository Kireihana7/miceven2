# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime



class ProductionOrder(models.Model):
    _inherit = 'mrp.production'

    mro_requests = fields.One2many('mro.request', 'production_id', string='MRO Requests', copy=False, readonly=True)
    mro_requests_count = fields.Integer("Number of MRO Requests", compute='_compute_mro_requests_count')


    def _compute_mro_requests_count(self):
        for order in self:
            order.mro_requests_count = len(order.mro_requests)
        return True

    def action_view_mro_requests(self):
        result = self.env["ir.actions.actions"]._for_xml_id('mro_maintenance.action_requests')
        mro_requests_ids = self.mro_requests
        if not mro_requests_ids or len(mro_requests_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (mro_requests_ids.ids)
        elif len(mro_requests_ids) == 1:
            view = self.env.ref('mro_maintenance.mro_request_form_view', False)
            form_view = [(view and view.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = mro_requests_ids.id
        return result
