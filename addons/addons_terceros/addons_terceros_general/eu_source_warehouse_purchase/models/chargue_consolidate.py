# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
    
class ChargueConsolidate(models.Model):
    _inherit = 'chargue.consolidate'

    # purchase_source_warehouse_id = fields.Many2one('purchase.source.warehouse', related="purchase_id.purchase_source_warehouse_id", string="Almacén Origen", store=True, tracking=True)
    purchase_source_warehouse_id = fields.Many2one(
        'purchase.source.warehouse', 
        compute='_compute_purchase_source_warehouse_id', 
        # inverse='_inverse_purchase_source_warehouse_id', 
        store=True,
        readonly=False,
        string="Almacén Origen",
        tracking=True
    )

    vehicle_owner = fields.Many2one('res.partner', related="vehicle_id.vehicle_owner", string="Propietario", store=True, tracking=True)

    # Obtener Contacto desde la Compra
    # @api.onchange('purchase_id')
    # def onchange_purchase_id(self):
    #     for rec in self:
    #         po = rec.purchase_id
            
    #         if po:
    #             rec.update({
    #                 "partner_id": po.partner_id.id,
    #                 "vehicle_id": po.vehicle_id.id,
    #                 "origin": po.name,
    #                 "purchase_source_warehouse_id": po.purchase_source_warehouse_id.id, # UPDATE
    #             })

    @api.onchange("operation_type")
    def _onchange_operation_type(self):
        for rec in self:
            if rec.is_pesaje_externo:
                rec.partner_id = None    

            # UPDATE:
            rec.purchase_id = None
            rec.purchase_source_warehouse_id = None                        

    @api.depends('operation_type', 'purchase_id', 'purchase_id.purchase_source_warehouse_id')
    def _compute_purchase_source_warehouse_id(self):
        for rec in self:
            if not rec.purchase_source_warehouse_id:
                rec.purchase_source_warehouse_id = False
            if rec.operation_type == 'compra':
                po = rec.purchase_id
                if po:
                    rec.purchase_source_warehouse_id = po.purchase_source_warehouse_id.id
                else:
                    rec.purchase_source_warehouse_id = False