# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class QualityCheck(models.Model):
    _inherit = "quality.check"

    partner_id = fields.Many2one(
        related='picking_id.partner_id', string='Socio',store=True)
    chargue_consolidate = fields.Many2one(related="picking_id.chargue_consolidate_create",string="Orden Romana",store=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle", 
        string="Vehículo", 
        compute="_compute_vehicle_id",
        tracking=True
    )
    license_plate = fields.Char("Licencia", related="vehicle_id.license_plate",store=True)

    @api.depends("chargue_consolidate.vehicle_id","picking_id.vehicle_id",)
    def _compute_vehicle_id(self):
        for rec in self:
            rec.vehicle_id = rec.chargue_consolidate.vehicle_id or rec.picking_id.vehicle_id

    def do_pass(self):
        res = super().do_pass()

        if self.chargue_consolidate:
            self.chargue_consolidate.write({
                "is_approved": True,
                "with_obs": False,
            })

        return res

    def do_fail(self):
        res = super().do_fail()
        
        if self.chargue_consolidate:
            self.chargue_consolidate.write({
                "is_approved": False,
                "with_obs": True,
            })

        return res
    
class QualityPoint(models.Model):
    _inherit = "quality.point"

    def _get_checks_values(self, products, company_id, existing_checks=False):
        res = super()._get_checks_values(products, company_id, existing_checks=existing_checks)

        if self._context.get("chargue_consolidate"):
            res["chargue_consolidate"] = self._context["chargue_consolidate"]

        return res