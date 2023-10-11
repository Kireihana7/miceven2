# -*- coding: utf-8 -*-

from datetime import date
import json
from typing import List
from odoo import models, fields, api
from odoo.exceptions import UserError

sql_tuple = lambda t: "({})".format(",".join(map(str, t)) or "'0'")
datestr = lambda s: f"'{s}'" if s else "NULL"
                                    
# Subcategorias
class KpiBranchCategory(models.Model):
    _inherit = "kpi.branch.category"

    zone_id = fields.Many2one(related="kpi_branch_id.zone_id")
    tipo_kpi = fields.Selection(related="kpi_branch_id.tipo_kpi")
    

class KpiSalespersonCategory(models.Model):
    _inherit = "kpi.salesperson.category"

    zone_id = fields.Many2one(related="kpi_salesperson_id.kpi_branch_id.zone_id")
    tipo_kpi = fields.Selection(related="kpi_salesperson_id.kpi_branch_id.tipo_kpi")

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
        "zone_id",
        # Salesperson
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.start_date",
        "kpi_salesperson_id.kpi_branch_id.kpi_kg_config_id.end_date",
        "kpi_salesperson_id.salesperson_id.branch_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.user_id",
        "kpi_salesperson_id.salesperson_id.branch_id.crm_team_ids.member_ids",
        "kpi_salesperson_id.salesperson_id.zone_id",
        "kpi_salesperson_id.salesperson_id.zone_id.crm_team_ids.user_id",
        "kpi_salesperson_id.salesperson_id.zone_id.crm_team_ids.member_ids",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.zone_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.date",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.state",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.categ_id",
        "kpi_salesperson_id.salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
        "tipo_kpi",
    )
    def _compute_progress(self):
        for rec in self:
            salesperson = rec.kpi_salesperson_id

            branch = rec.branch_id.id
            zone = rec.zone_id.id

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

            if branch and tipo_kpi == 'branch':
                query += f"AND am.branch_id = {branch}"

            if zone and tipo_kpi == 'zona'::
                query += f"AND am.zone_id = {zone}"

            query += "GROUP BY am.move_type ORDER BY am.move_type"
            
            self.env.cr.execute(query)

            move_ids = self.env.cr.dictfetchall()

            if not move_ids:
                rec.progress = 0
                continue

            rec.progress = move_ids[0]["weight"]
            
            if len(move_ids) == 2:
                rec.progress -= move_ids[1]["weight"]

    #endregion
    