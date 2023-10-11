# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    chargue_consolidate_ids = fields.Many2many(
        "chargue.consolidate",
        "chargue_consolidate_sale_order_rel",
        "sale_order_id",
        "consolidate_id",
        string="Órdenes de carga",
        readonly=True,
        tracking=True,
    )
    chargue_consolidate_count = fields.Integer("Ordenes de Carga", compute='_compute_chargue_consolidate_count')
    vehicle_id = fields.Many2one('fleet.vehicle', "Vehículo", tracking=True)
    driver_id = fields.Many2one('res.partner', "Conductor",store=True)
    vehicle_type_property = fields.Selection(related='vehicle_id.vehicle_type_property', store=True)
    license_plate = fields.Char("Licencia", related="vehicle_id.license_plate", store=True)

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        self.update({"driver_id": self.vehicle_id.driver_id.id})

    @api.depends("chargue_consolidate_ids")
    def _compute_chargue_consolidate_count(self):
        for rec in self:
            rec.chargue_consolidate_count = len(rec.chargue_consolidate_ids)

    def open_chargue_consolidate(self):
        self.ensure_one()

        return {
            "name": "Ordenes",
            "type": "ir.actions.act_window",
            "res_model": "chargue.consolidate",
            "view_mode": "tree,form,kanban,graph",
            "target": "current",
            "context": {
                "create": False,
            },
            "domain": [("id", "in", self.chargue_consolidate_ids.ids)]
        }

    def action_confirm(self):
        res = super().action_confirm()

        if not self.order_line:
            raise Warning(_('Por favor, agrega al menos un producto a la Venta.'))

        if self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.create_order_so", False) and \
            self.chargue_consolidate_count == 0 and \
            self.order_line.product_id.filtered("need_romana"):
            consolidate_obj = self.env['chargue.consolidate']

            chargue_consolidate = consolidate_obj.sudo().create({
                'scheduled_date': self.commitment_date or fields.Datetime.now(),
                'vehicle_id': self.vehicle_id.id,
                'sale_ids': self.ids,
                'operation_type': 'venta',
                'state': 'por_llegar',
                'partner_id': self.partner_id.id,
                'origin': self.name,
                'picking_id': self.picking_ids.ids,
                'with_trailer': self.vehicle_id.with_trailer,
                'plate_trailer': self.vehicle_id.plate_trailer,
                'company_id': self.company_id.id,
            })

            self.picking_ids.write({
                "vehicle_id": self.vehicle_id.id,
                "chargue_consolidate_create": chargue_consolidate.id,
            })
            
        return res

    def _prepare_invoice(self):
        self.ensure_one()

        res: dict = super()._prepare_invoice()

        res.update({
            "driver_id": self.driver_id.id,
            "vehicle_id": self.vehicle_id.id,
        })

        return res