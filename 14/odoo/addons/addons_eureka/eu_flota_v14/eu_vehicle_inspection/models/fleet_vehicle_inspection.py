# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicleInspection(models.Model):
    _name = "fleet.vehicle.inspection"
    _description = "Inspección vehícular"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Código", tracking=True,)
    inspection_date = fields.Date("Fecha de Inspeccion", tracking=True,)
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehiculo", tracking=True,)
    odometer = fields.Float("Último Odómetro", related="vehicle_id.odometer", tracking=True,)
    vechical_type_id = fields.Many2one("vehicle.type", "Tipo de Vehiculo", related="vehicle_id.vechical_type_id", tracking=True,)
    driver_id = fields.Many2one("res.partner", "Conductor", related="vehicle_id.driver_id", tracking=True,)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "attachment_inspection_rel",
        "inspection_id",
        "attachment_id",
        "Archivos",
        tracking=True,
    )
    observation = fields.Text("Observación", tracking=True)
    state = fields.Selection([
        ("borrador", "Borrador"),
        ("en_proceso", "En proceso"),
        ("confirmada", "Confirmada"),
    ], "Estatus", default="borrador", tracking=True)
    inspection_line_ids = fields.One2many("fleet.inspection.line", "inspection_id", "Inspecciones", tracking=True)

    @api.onchange("state")
    def _onchange_state(self):
        InspectionLine = self.env["fleet.inspection.line"]
        category_ids = self.env["fleet.inspection.category"].search([])

        for rec in self:
            if (rec.state == "borrador") and (not rec.inspection_line_ids):
                for category in category_ids:
                    parent_id =  InspectionLine.create({
                        "name": category.name,
                        "display_type": "line_section",
                        "inspection_id": rec.id,
                    })

                    for part in category.inspection_part_ids:
                        InspectionLine.create({
                            "name": part.name,
                            "inspection_id": rec.id,
                            "part_id": part.id,
                            "category_id": category.id,
                            "parent_id": parent_id.id
                        })

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        Sequence = self.env["ir.sequence"]
        CODE = "inspection.order"
        COMPANY = self.env.company

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "INSP/",
                'name': f"Ficha de inspección en {COMPANY.name}",
                'padding': 4,
                'company_id': COMPANY.id,
            })

        res.write({"name": Sequence.next_by_code(CODE) })

        return res


    def action_report_ficha_inspection(self):
        return self.env \
            .ref("eu_vehicle_inspection.custom_action_report_ficha_inspection") \
            .report_action(self)