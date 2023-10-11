# -*- coding: utf-8 -*-

from datetime import date
import json
from typing import List
from odoo import models, fields, api
from odoo.exceptions import UserError

sql_tuple = lambda t: "({})".format(",".join(map(str, t)) or "'0'")
datestr = lambda s: f"'{s}'" if s else "NULL"
                                    
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
    weight_percent = fields.Float("Peso %",tracking=True)
    max_percent = fields.Float("Tope %",tracking=True)
    
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
    branch_id = fields.Many2one(related="kpi_salesperson_id.kpi_branch_id.branch_id")

    progress = fields.Float(
        "Progreso",
        compute="_compute_progress",
        tracking=True,
        store=True,
    )
    actual_percent = fields.Float(
        "Logro Volumen %",
        compute="_compute_logro",
        tracking=True,
        store=True
    )
    kpi_percent = fields.Float(
        "KPI %",
        compute="_compute_kpi_percent",
        tracking=True,
        store=True
    )
    kpi_amount = fields.Float(
        "Valor",
        compute="_compute_kpi_percent",
        tracking=True,
        store=True
    )
    kpi_monto_logrado = fields.Float(
        "Bono",
        compute="_compute_kpi_percent",
        tracking=True,
        store=True
    )
    kpi_category_id_domain = fields.Char(
        compute="_compute_kpi_category_id_domain",
        readonly=True,
        store=False,
    )
    
    @api.depends(
        "kpi_salesperson_id.kpi_branch_id.kpi_subcategory_ids.kpi_category_id",
        "kpi_salesperson_id.kpi_subcategory_ids.kpi_category_id",
    )
    def _compute_kpi_category_id_domain(self):
        for rec in self:
            salesperson = rec.kpi_salesperson_id

            ids = salesperson.kpi_branch_id.kpi_subcategory_ids.kpi_category_id
            ids -= salesperson.kpi_subcategory_ids.kpi_category_id

            rec.kpi_category_id_domain = json.dumps([("id","in", ids.ids)])

    #region Computes
    @api.depends(
        "kpi_category_id.categ_ids",
        "branch_id",

        # Salesperson
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.start_date",
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.end_date",
        "kpi_salesperson_id.salesperson_id.branch_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.user_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.member_ids",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.date",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.state",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.categ_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
    )
    def _compute_progress(self):
        for rec in self:
            salesperson = rec.kpi_salesperson_id

            branch = rec.branch_id.id
            dates: dict[str, date] = salesperson.kpi_kg_config_id.date_range
            user_ids: list[int] = salesperson.get_invoice_user_ids()
            
            query = f"""
SELECT SUM(pp.weight * aml.quantity) AS weight
FROM account_move_line aml
RIGHT JOIN account_move am ON aml.move_id = am.id 
RIGHT JOIN product_product pp ON aml.product_id = pp.id
WHERE 
    am.move_type in ('out_invoice','out_refund') AND
    am.state = 'posted' AND
    aml.categ_id IN {sql_tuple(rec.kpi_category_id.categ_ids.ids)} AND
    am.date >= {datestr(dates["start"])} AND
    am.date <= {datestr(dates["end"])}
"""

            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"

            if branch:
                query += f"AND am.branch_id = {branch}"

            query += "GROUP BY am.move_type ORDER BY am.move_type"
            
            self.env.cr.execute(query)

            move_ids = self.env.cr.dictfetchall()

            if not move_ids:
                rec.progress = 0
                continue

            rec.progress = move_ids[0]["weight"]
            
            if len(move_ids) == 2:
                rec.progress -= move_ids[1]["weight"]

    @api.depends('progress', 'goal')
    def _compute_logro(self):
        for rec in self:
            rec.actual_percent =  (rec.progress / (rec.goal or 1)) * 100

    @api.depends(
        "kpi_kg_config_id.kpi_tabla.salesman_bonification",
        "kpi_kg_config_id.kpi_tabla.manager_bonification",
        "kpi_kg_config_id.kpi_tabla.branch_manager_bonification",
        "kpi_kg_config_id.kpi_tabla.national_manager_bonification",
        "kpi_kg_config_id.kpi_tabla.line_ids.numero",
        "kpi_salesperson_id.category_active",
        "kpi_kg_config_id.kpi_tabla.line_ids.volumen",
        "kpi_kg_config_id.kpi_tabla.volumen_min",
        "kpi_category_id.weight_percent",
        "kpi_category_id.max_percent",
    )
    def _compute_kpi_percent(self):
        for rec in self:
            monto = rec.get_bonificacion_domain_by_rank()
            
            volumen = rec.kpi_kg_config_id \
                .kpi_tabla \
                .line_ids \
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
            elif monto_logrado >= tope:
                rec.kpi_monto_logrado = tope
    #endregion
    
    def get_bonificacion_domain_by_rank(self):
        self.ensure_one()

        tabla = self.kpi_kg_config_id.kpi_tabla
        monto = 0
        
        if self.kpi_salesperson_id.rank == "vendedor":
            monto = tabla.salesman_bonification
        elif self.kpi_salesperson_id.rank == "coordinador":
            monto = tabla.manager_bonification  
        elif self.kpi_salesperson_id.rank == "gerente_sucursal":
            monto = tabla.branch_manager_bonification
        elif self.kpi_salesperson_id.rank == "gerente_nacional":
            monto = tabla.national_manager_bonification
        
        return monto