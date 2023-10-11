# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    # @api.multi #odoo13
    def show_mpr_fleet_action(self):
        self.ensure_one()
        res = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
        res = res.read()[0]
        res['domain'] = str([('custom_fleet_id', '=', self.id)])
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
