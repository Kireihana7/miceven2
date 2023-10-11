# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

VENDEDOR = lambda x: x.rank == 'vendedor'

class KpiConfigBranch(models.Model):
    _name = "kpi.config.branch"
    _description = " Sucursales del KPI por kilogramo"
    _inherit = 'kpi.mixin'

    name = fields.Char("Nombre", related="branch_id.name", tracking=True,)
    branch_id = fields.Many2one("res.branch", "Sucursal", tracking=True,)
    kpi_kg_config_id = fields.Many2one("kpi.kg.config", "KPI", ondelete="cascade", tracking=True,)
    kpi_salesperson_ids = fields.One2many("kpi.config.salesperson", "kpi_branch_id", "Vendedores", tracking=True,)
    kpi_subcategory_ids = fields.One2many("kpi.branch.category", "kpi_branch_id", "Categorias", tracking=True)
    salesperson_goal = fields.Float(
        "Meta distribuida vendedores",
        compute="_compute_salesperson_goal",
        store=True,
        tracking=True,
    )

    #region Constrains
    @api.constrains("kpi_salesperson_ids")
    def _check_kpi_salesperson_ids(self):
        for rec in self:
            if round(sum(rec.kpi_salesperson_ids.filtered(VENDEDOR).mapped("goal")),2) > round(rec.goal,2):
                raise ValidationError(" ".join([
                    "La meta fue distribuida de forma",
                    "incorrecta entre los vendedores de la sucursal",
                    rec.name,
                ]))

    @api.constrains("branch_id")
    def _check_branch_id(self):
        for rec in self:
            if not rec.branch_id.manager_id:
                raise ValidationError("La sucursal no posee manager")
    #endregion

    #region Computes
    @api.depends("kpi_subcategory_ids.goal")
    def _compute_distributed_goal(self):
        for rec in self:
            rec.distributed_goal = sum(rec.kpi_subcategory_ids.mapped("goal"))

    @api.depends("kpi_salesperson_ids.goal","kpi_salesperson_ids.rank")
    def _compute_salesperson_goal(self):
        for rec in self:
            rec.salesperson_goal = sum(rec.kpi_salesperson_ids.filtered(VENDEDOR).mapped("goal"))

    @api.depends("kpi_salesperson_ids.progress","kpi_salesperson_ids.rank")
    def _compute_progress(self):
        for rec in self:
            rec.progress = sum(rec.kpi_salesperson_ids.filtered(VENDEDOR).mapped("progress"))
    #endregion

    @api.onchange("kpi_kg_config_id")
    def _onchange_kpi_kg_config_id(self):
        self.ensure_one()

        return {
            "domain": {
                "kpi_categ_id": [("id", "in", self.kpi_kg_config_id.kpi_categ_ids.ids)]
            }
        }

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            gerente_id = rec.kpi_salesperson_ids.create({
                "salesperson_id": rec.branch_id.manager_id.id,
                "kpi_branch_id": rec.id,
                "rank": "gerente_sucursal",
                "kpi_kg_config_id": rec.kpi_kg_config_id.id,
                "parent_id": rec.kpi_kg_config_id \
                    .kpi_salesperson_id \
                    .filtered(lambda s: s.rank == "gerente_nacional") \
                    .id
            })

            team_ids = self.env["crm.team"] \
                .sudo() \
                .search([("branch_id", "=", rec.branch_id.id)])

            team_ids._check_for_employee()

            for team in team_ids:
                coordinador_id = rec.kpi_salesperson_ids.create({
                    "salesperson_id": team.user_id
                        .employee_ids
                        .filtered(lambda e: e.company_id == self.env.company)[0] \
                        .id,
                    "kpi_branch_id": rec.id,
                    "kpi_kg_config_id": rec.kpi_kg_config_id.id,
                    "rank": "coordinador",
                    "crm_team_id": team.id,
                    "parent_id": gerente_id.id,
                })
            
                rec.kpi_salesperson_ids.create([{
                    "salesperson_id": member.id,
                    "kpi_branch_id": rec.id,
                    "kpi_kg_config_id": rec.kpi_kg_config_id.id,
                    "rank": "vendedor",
                    "crm_team_id": team.id,
                    "parent_id": coordinador_id.id,
                } for member in team.member_ids.employee_id])

        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        compute = {'salesperson_goal', 'goal', 'distributed_goal', 'progress'}

        if not compute - set(fields):
            return res
        
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])

                for field in compute:
                    group['salesperson_goal'] = sum(getattr(quant, field) for quant in quants)

        return res