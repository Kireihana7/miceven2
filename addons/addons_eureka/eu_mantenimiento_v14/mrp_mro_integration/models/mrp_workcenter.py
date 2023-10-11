# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'


    STATE_SELECTION = [
        ('ready', 'READY'),
        ('on_maintenance', 'ON MAINTENANCE'),
    ]

    equipment_id = fields.Many2one('mro.equipment', 'Equipment', domain="[('company_id','=', company_id)]", copy=False)
    mro_orders_count = fields.Integer("Number of MRO Orders", compute='_compute_mro_orders_count')
    mro_requests_count = fields.Integer("Number of MRO Requests", compute='_compute_mro_requests_count')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, default='ready')
    periodic_maintenance = fields.Boolean('Periodic Maintenance', copy=False)
    meter_id = fields.Many2one('mro.meter', 'Meter', related='equipment_id.meter_id')

    @api.onchange("equipment_id")
    def onchange_equipment_id(self):
        if not self.equipment_id:
            self.periodic_maintenance = False

    @api.constrains('equipment_id')
    def check_equipemnt_unique(self):
        workcenters = self.env['mrp.workcenter'].search([('equipment_id', '=', self.equipment_id.id)])
        if self.equipment_id and len(workcenters) > 1:
            raise UserError(_("Equipment already assigned"))
        return True

    def _compute_mro_orders_count(self):
        order = self.env['mro.order']
        for workcenter in self:
            workcenter.mro_orders_count = order.search_count([('equipment_id', '=', workcenter.equipment_id.id)])
        return True

    def action_view_mro_orders(self):
        context = {'search_default_equipment_id': [self.equipment_id.id],'default_equipment_id': self.equipment_id.id,}
        return {
            'domain': "[('equipment_id','in',[" + ','.join(map(str, self.equipment_id.ids)) + "])]",
            'context': context,
            'name': _('Maintenance Orders'),
            'views': [(self.env.ref('mro_maintenance.mro_order_tree_view').id, "tree"), (self.env.ref('mro_maintenance.mro_order_form_view').id, "form")],
            'res_model': 'mro.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def _compute_mro_requests_count(self):
        request = self.env['mro.request']
        for workcenter in self:
            workcenter.mro_requests_count = request.search_count([('equipment_id', '=', workcenter.equipment_id.id)])
        return True

    def action_view_mro_requests(self):
        context = {'search_default_equipment_id': [self.equipment_id.id],'default_equipment_id': self.equipment_id.id,}
        return {
            'domain': "[('equipment_id','in',[" + ','.join(map(str, self.equipment_id.ids)) + "])]",
            'context': context,
            'name': _('Maintenance Requests'),
            'views': [(self.env.ref('mro_maintenance.mro_request_tree_view').id, "tree"), (self.env.ref('mro_maintenance.mro_request_form_view').id, "form")],
            'res_model': 'mro.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }