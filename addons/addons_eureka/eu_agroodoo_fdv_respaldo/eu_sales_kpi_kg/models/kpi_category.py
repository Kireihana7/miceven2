# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError

class KpiConfigCategoryGroup(models.Model):
    _name = "kpi.config.category.group"
    _description = "Grupo de categorias para KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre de la Familia", tracking=True,)
    categ_ids = fields.Many2many(
        "product.category", 
        "kpi_config_categ_rel", 
        "group_id", 
        "categ_id", 
        "Grupos de categoría",
        tracking=True,
    )
    kpi_kg_config_id = fields.Many2one("kpi.kg.config", "KPI", ondelete="cascade", tracking=True,)
    weight_percent = fields.Float(string="Peso %",tracking=True)
    max_percent = fields.Float(string="Tope %",tracking=True)
    
    @api.onchange("kpi_kg_config_id")
    def _onchange_kpi_kg_config_id(self):
        self.ensure_one()

        return {
            "domain": {
                "categ_ids": [("id", "not in", self.kpi_kg_config_id.kpi_categ_ids.categ_ids.ids)],
            }
        }

# Subcategorias
class KpiBranchCategory(models.Model):
    _name = "kpi.branch.category"
    _description = "Categoria de sucursal"
    _inherit = 'kpi.sub.category'

    kpi_branch_id = fields.Many2one("kpi.config.branch", "Sucursal", tracking=True)
    kpi_kg_config_id = fields.Many2one("kpi.kg.config",related="kpi_branch_id.kpi_kg_config_id",store=True)
    branch_id = fields.Many2one(related="kpi_branch_id.branch_id")
    
    @api.onchange("kpi_branch_id")
    def _onchange_kpi_kg_config_id(self):
        self.ensure_one()

        branch = self.kpi_branch_id

        ids = set(branch.kpi_kg_config_id.kpi_categ_ids.ids)

        if branch.kpi_subcategory_ids:
            ids -= set(branch.kpi_subcategory_ids.mapped("kpi_category_id.id"))

        return {
            "domain": {
                "kpi_category_id":  [("id", "in", list(ids))]
            }
        }

class KpiSalespersonCategory(models.Model):
    _name = "kpi.salesperson.category"
    _description = "Categoria del vendedor"
    _inherit = 'kpi.sub.category'

    kpi_salesperson_id = fields.Many2one("kpi.config.salesperson", "Sucursal", tracking=True)
    kpi_kg_config_id = fields.Many2one("kpi.kg.config",related="kpi_salesperson_id.kpi_kg_config_id",store=True)
    progress = fields.Float("Progreso", compute="_compute_progress", default=0, tracking=True)
    actual_percent = fields.Float(string="Logro Volumen %",compute="_compute_logro",tracking=True)
    kpi_percent = fields.Float(string="KPI %",compute="_compute_kpi_percent",tracking=True)
    kpi_amount = fields.Float(string="Valor",compute="_compute_kpi_percent",tracking=True)
    kpi_monto_logrado = fields.Float(string="Bono",compute="_compute_kpi_percent",tracking=True)
    branch_id = fields.Many2one(related="kpi_salesperson_id.kpi_branch_id.branch_id")
    
    @api.onchange("kpi_salesperson_id")
    def _onchange_kpi_kg_config_id(self):
        self.ensure_one()

        FILTER = "kpi_category_id.id"

        salesperson = self.kpi_salesperson_id

        ids = salesperson \
            .kpi_branch_id \
            .kpi_subcategory_ids \
            .mapped(FILTER)

        ids = set(ids)

        if salesperson.kpi_subcategory_ids:
            ids -= set(salesperson.kpi_subcategory_ids.mapped(FILTER))

        return {
            "domain": {
                "kpi_category_id":  [("id", "in", list(ids))]
            }
        }
    
    #region Computes
    @api.depends(
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.start_date",
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.end_date",
        "kpi_salesperson_id.salesperson_id.user_id",
        "kpi_salesperson_id.salesperson_id.branch_id",
        "kpi_category_id.categ_ids",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.categ_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
        "kpi_salesperson_id.crm_team_id.user_id",
        "kpi_salesperson_id.crm_team_id.member_ids",
        "kpi_salesperson_id.salesperson_id.branch_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.user_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.member_ids",
    )
    def _compute_progress(self):
        for rec in self:
            salesperson = rec.kpi_salesperson_id

            dates: dict[str, date] = salesperson.kpi_kg_config_id.date_range

            domain = [
                ("state", "=", "posted"),
                ("date", ">=", dates["start"]),
                ("date", "<=", dates["end"]),
            ]
            if salesperson.rank !='gerente_nacional':
                domain += salesperson.get_invoice_domain_by_rank()
            filtered_callback = lambda l: l.product_id.categ_id.id in rec.kpi_category_id.categ_ids.ids
            mapped_callback = lambda l: l.product_id.weight * l.quantity

            move_ids = self.env["account.move"].sudo() \
                .search([
                    *domain,
                    ("move_type", "=", "out_invoice"),
                ]) \
                .mapped('invoice_line_ids') \
                .filtered(filtered_callback) \
                .mapped(mapped_callback)  

            move_ids_refund = self.env["account.move"].sudo() \
                .search([
                    *domain,
                    ("move_type", "=", "out_refund"),
                ]) \
                .mapped("invoice_line_ids") \
                .filtered(filtered_callback) \
                .mapped(mapped_callback) 

            if not move_ids:
                rec.progress = 0
                continue

            rec.progress = sum(move_ids) - sum(move_ids_refund)

    @api.depends('progress', 'goal')
    def _compute_logro(self):
        for rec in self:
            rec.actual_percent =  (rec.progress / (rec.goal or 1)) * 100

    @api.depends(
        "kpi_kg_config_id.kpi_tabla.volumen_min",
        "kpi_salesperson_id.bonification",
        "kpi_salesperson_id.category_active",
        "kpi_kg_config_id.kpi_tabla.line_ids.numero",
        "kpi_kg_config_id.kpi_tabla.line_ids.volumen",
        "kpi_category_id.weight_percent",
        "kpi_category_id.max_percent",
    )
    def _compute_kpi_percent(self):
        for rec in self:
            monto = rec.get_bonificacion_domain_by_rank()
            
            volumen = rec.kpi_kg_config_id \
                .kpi_tabla.line_ids \
                .filtered(lambda x: x.numero == rec.kpi_salesperson_id.category_active) \
                .mapped('volumen')
            volumen = sum(volumen)

            volumen_min = rec.kpi_kg_config_id.kpi_tabla.volumen_min
            peso = rec.kpi_category_id.weight_percent

            RESULT = (peso * volumen) / 100 
            MONTO_RESULT = (monto * RESULT) / 100

            rec.kpi_percent = RESULT
            rec.kpi_amount = monto_kpi = MONTO_RESULT
            
            monto_logrado = MONTO_RESULT * (rec.actual_percent / 100)

            tope = (monto_kpi * rec.kpi_category_id.max_percent) / 100

            minimo = (monto_kpi * volumen_min) / 100
            rec.kpi_monto_logrado = 0

            if (monto_logrado >= minimo) and (monto_logrado < tope):
                rec.kpi_monto_logrado = monto_logrado
            elif monto_logrado > tope:
                rec.kpi_monto_logrado = tope
    #endregion
    
    def get_bonificacion_domain_by_rank(self):
        self.ensure_one()
        domain = []
        monto = 0
        if self.kpi_salesperson_id.rank == "vendedor":
            monto = self.kpi_kg_config_id.kpi_tabla.salesman_bonification
        
        if self.kpi_salesperson_id.rank == "coordinador":
            monto = self.kpi_kg_config_id.kpi_tabla.manager_bonification
            
        if self.kpi_salesperson_id.rank == "gerente_sucursal":
            monto = self.kpi_kg_config_id.kpi_tabla.branch_manager_bonification

        if self.kpi_salesperson_id.rank == "gerente_nacional":
            monto = self.kpi_kg_config_id.kpi_tabla.national_manager_bonification
            
        
        return monto