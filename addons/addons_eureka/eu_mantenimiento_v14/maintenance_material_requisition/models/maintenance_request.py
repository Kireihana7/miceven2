# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    
    def show_maintenance_action(self):
        self.ensure_one()
        res = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
        res = res.read()[0]
        res['domain'] = str([('custom_maintenance_id', '=', self.id)])
        return res
