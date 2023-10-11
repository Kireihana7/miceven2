# -*- coding: utf-8 -*-

from odoo import models, fields
class FleetInspectionCategory(models.Model):
    _name = "fleet.inspection.category"
    _description = "Categoría de inspección"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", tracking=True)
    inspection_part_ids = fields.One2many("fleet.inspection.part", "category_id", "Partes", tracking=True)

class FleetInspectionPart(models.Model):
    _name = "fleet.inspection.part"
    _description = "Partes de inspección"

    name = fields.Char("Nombre")
    category_id = fields.Many2one("fleet.inspection.category", "Categoría",)

class FleetInspectionLine(models.Model):
    _name = "fleet.inspection.line"
    _description = "Líneas de inspección"

    name = fields.Char("Nombre")
    part_id = fields.Many2one("fleet.inspection.part", "Parte")
    category_id = fields.Many2one("fleet.inspection.category", "Categoría", related="part_id.category_id")
    state = fields.Selection([
        ("bueno", "Bueno"),
        ("medio", "Medio"),
        ("deficiente", "Deficiente"),
        ("nm", "NM"),
    ], "Estatus", default="bueno")
    display_type = fields.Selection([('line_section', 'Sección'),('line_note', 'Nota'),], default=False)
    inspection_id = fields.Many2one("fleet.vehicle.inspection", "Ficha de inspección")

    parent_id = fields.Many2one("fleet.inspection.line")