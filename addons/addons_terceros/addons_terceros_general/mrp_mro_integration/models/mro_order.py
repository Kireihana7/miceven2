# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class MroOrder(models.Model):
    _inherit = 'mro.order'


    @api.constrains('state')
    def _compute_workcenter_status(self):
        for order in self:
            workcenter = self.env['mrp.workcenter'].search([('equipment_id', '=', order.equipment_id.id)], limit=1)
            if workcenter:
                active_mro_orders = self.search([('equipment_id', '=', order.equipment_id.id), ('state', 'not in', ('draft','done', 'cancel'))])
                if active_mro_orders:
                    workcenter.state = 'on_maintenance'
                else:
                    workcenter.state = 'ready'
        return True
