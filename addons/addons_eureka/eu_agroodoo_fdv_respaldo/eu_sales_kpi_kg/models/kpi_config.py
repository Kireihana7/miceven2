# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class KpiConfigBranch(models.Model):
    _name = "kpi.config.branch"
    _description = " Sucursales del KPI por kilogramo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", related="branch_id.name", tracking=True,)
    branch_id = fields.Many2one("res.branch", "Sucursal", tracking=True,)
    manager_id = fields.Many2one("res.users", "Manager", related="branch_id.manager_id", tracking=True,)
    kpi_categ_id = fields.Many2one("kpi.config.category.group", "Categoria", tracking=True,)
    is_active = fields.Boolean("Activa", tracking=True,)
    monthly_goal = fields.Float("Meta", related="kpi_categ_id.objetivo", tracking=True,)
    kpi_kg_config_id = fields.Many2one("kpi.kg.config", "KPI", ondelete="cascade", tracking=True,)
    kpi_salesperson_ids = fields.One2many("kpi.config.salesperson", "kpi_branch_id", "Vendedores", tracking=True,)

    @api.constrains("monthly_goal", "kpi_salesperson_ids")
    def _check_monthy_goal(self):
        for rec in self:
            if sum(rec.kpi_salesperson_ids.mapped("monthly_goal")) != rec.monthly_goal:
                raise ValidationError("La meta mensual no está distribuida correctamente")

    #region Onchanges
    @api.onchange("branch_id")
    def _onchange_branch_id(self):
        for rec in self:
            if not rec.branch_id:
                continue

            rec.kpi_salesperson_ids.unlink()

            salesperson_ids = rec.branch_id.salesperson_ids.ids

            if not salesperson_ids:
                raise UserError("La sucursal no posee ningún vendedor")

            rec.kpi_salesperson_ids.create([{
                "salesperson_id": employee_id,
                "kpi_branch_id": rec.id,
            } for employee_id in salesperson_ids])

    @api.onchange("kpi_kg_config_id")
    def _onchange_kpi_kg_config_id(self):
        self.ensure_one()

        return {
            "domain": {
                "kpi_categ_id": [("id", "in", self.kpi_kg_config_id.kpi_categ_ids.ids)]
            }
        }
    #endregion

class KpiConfigCategoryGroup(models.Model):
    _name = "kpi.config.category.group"
    _description = "Grupo de categorias para KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre de la categoria", tracking=True,)
    categ_ids = fields.Many2many(
        "product.category", 
        "kpi_config_categ_rel", 
        "group_id", 
        "categ_id", 
        "Grupos de categoria",
        tracking=True,
    )
    kpi_kg_config_id = fields.Many2one("kpi.kg.config", "KPI", ondelete="cascade", tracking=True,)
    objetivo = fields.Float("Objetivo (Kg)", tracking=True,)

class KpiConfigSalesperson(models.Model):
    _name = "kpi.config.salesperson"
    _description = "Vendedores de KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", related="salesperson_id.name", tracking=True,)
    salesperson_id = fields.Many2one("hr.employee", "Vendedor", tracking=True,)
    monthly_goal = fields.Float("Meta (Kg)", tracking=True,)
    kpi_branch_id = fields.Many2one("kpi.config.branch", "Sucursal", ondelete="cascade", tracking=True,)
    progress = fields.Float("Progreso", compute="_compute_progress", tracking=True,)

    @api.depends(
        "kpi_branch_id.kpi_kg_config_id.start_date",
        "kpi_branch_id.kpi_kg_config_id.end_date",
        "salesperson_id.user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
    )
    def _compute_progress(self):
        for rec in self:
            if not rec.kpi_branch_id.kpi_kg_config_id:
                rec.progress = 0
                continue

            dates: dict[str, date] = rec.kpi_branch_id.kpi_kg_config_id.date_range

            weights = self.env['account.move'].sudo() \
                .search([
                    ("state", "=", "posted"),
                    ("move_type", "=", "out_invoice"),
                    ("user_id", "=", rec.salesperson_id.user_id.id)
                ]) \
                .filtered(lambda x: dates["start"] <= x.date <= dates["end"]) \
                .mapped("invoice_line_ids") \
                .mapped("product_id.weight")

            rec.progress = sum(weights)