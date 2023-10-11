# -*- coding: utf-8 -*-

from pyexpat import model
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    chargue_consolidate = fields.One2many(
        comodel_name='chargue.consolidate',
        inverse_name='purchase_id',
        string='Ordenes de Descarga',
    )
    chargue_consolidate_count = fields.Integer("Ordenes de Carga", compute='_compute_chargue_consolidate_count')
    vehicle_id      = fields.Many2one('fleet.vehicle', string="Vehículo", tracking=True)
    vehicle_type_property    = fields.Selection(related='vehicle_id.vehicle_type_property',store=True)
    driver_id       = fields.Many2one('res.partner', related="vehicle_id.driver_id", string="Conductor",store=True)
    license_plate   = fields.Char(string="Licencia", related="vehicle_id.license_plate",store=True)
    aplicar_descuento = fields.Boolean(string="Aplicar Descuento",default=False)

    def _compute_chargue_consolidate_count(self):
        for rec in self:
            rec.chargue_consolidate_count = self.env['chargue.consolidate'].sudo().search_count([('purchase_id', '=', rec.id)])

    def open_chargue_consolidate(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Ordenes",
            "res_model": "chargue.consolidate",
            "view_mode": "tree,form,kanban,graph",
            "target": "current",
            "context": {
                "create": False,
            },
            "domain": [('purchase_id', '=', self.id)]
        }

    def get_consolidate_vals(self):
        return {
            'scheduled_date': self.date_planned or fields.Datetime.now(),
            'vehicle_id': self.vehicle_id.id,
            'purchase_id': self.id,
            'operation_type': 'compra',
            'state': 'por_llegar',
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'picking_id': self.picking_ids.ids,
            'with_trailer': self.vehicle_id.with_trailer,
            'plate_trailer': self.vehicle_id.plate_trailer,
            'company_id': self.company_id.id,   
            'aplicar_descuento':self.aplicar_descuento,
        }

    def button_confirm(self):
        res = super().button_confirm()

        for rec in self:
            if not rec.order_line:
                raise Warning(_('Por favor, agrega al menos un producto a la Compra.'))

            if self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.create_order_po", False) and \
                rec.chargue_consolidate_count == 0 and \
                self.order_line.product_id.filtered("need_romana"):
                self.env['chargue.consolidate'].sudo().create(rec.get_consolidate_vals())
                    
        return res

    def _prepare_invoice(self):
        self.ensure_one()

        res: dict = super()._prepare_invoice()

        res.update({
            "driver_id": self.driver_id.id,
            "vehicle_id": self.vehicle_id.id,
        })

        return res

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    peso_liquidar = fields.Float("Peso a liquidar")

    @api.model
    def create(self, vals_list):
        if not self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.peso_liquidar_po"):
            if type(vals_list) == dict:
                vals_list = [vals_list]

            for vals in vals_list:
                if not vals.get("product_qty") and vals.get("peso_liquidar"):
                    vals["product_qty"] = vals.get("peso_liquidar")

        return super().create(vals_list)

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move=move)

        if self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.peso_liquidar_po") and self.peso_liquidar:
            res["quantity"] = self.peso_liquidar
        if self.order_id.aplicar_descuento and self.peso_liquidar:
            res["quantity"] = self.peso_liquidar

        return res