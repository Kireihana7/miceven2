# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
        tracking=True,
    )
    progress_percent = fields.Float(string="Progreso %",compute="_compute_progress_percent")
    #region Constrains
    @api.constrains("kpi_salesperson_ids")
    def _check_kpi_salesperson_ids(self):
        for rec in self:
            if round(sum(rec.kpi_salesperson_ids.filtered(lambda x: x.rank == 'vendedor').mapped("goal")),2) > round(rec.goal,2):
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

    @api.depends("kpi_salesperson_ids.goal")
    def _compute_salesperson_goal(self):
        for rec in self:
            rec.salesperson_goal = sum(rec.kpi_salesperson_ids.filtered(lambda x:x.rank=='vendedor').mapped("goal"))

    @api.depends("kpi_salesperson_ids.progress")
    def _compute_progress(self):
        for rec in self:
            rec.progress = sum(rec.kpi_salesperson_ids.filtered(lambda x:x.rank=='vendedor').mapped("progress"))
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

            team_ids = self.env["crm.team"].search([("branch_id", "=", rec.branch_id.id)])

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

    @api.depends('progress','goal')
    def _compute_progress_percent(self):
        for rec in self:
            rec.progress_percent = 0
            if rec.progress != 0 and rec.goal != 0:
                rec.progress_percent = round((rec.progress * 100) / rec.goal,2)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'goal' not in fields or 'progress' not in fields:
            return super(KpiConfigBranch, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(KpiConfigBranch, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['goal'] = sum(quant.goal for quant in quants)
                group['progress'] = sum(quant.progress for quant in quants)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'salesperson_goal' not in fields or 'goal' not in fields or 'distributed_goal' not in fields or 'progress' not in fields:
            return super(PurchaseOrder, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(PurchaseOrder, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['salesperson_goal'] = sum(quant.salesperson_goal for quant in quants)
                group['goal'] = sum(quant.goal for quant in quants)
                group['distributed_goal'] = sum(quant.distributed_goal for quant in quants)
                group['progress'] = sum(quant.progress for quant in quants)
        return res