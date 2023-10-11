# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError

class KpiSubCategory(models.AbstractModel):
    _name = "kpi.sub.category"
    _description = "Facturables de accion"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre de la categoría", related="kpi_category_id.name", tracking=True)
    kpi_category_id = fields.Many2one("kpi.config.category.group", "Categoria", tracking=True)
    goal = fields.Float("Meta (Kg)", tracking=True,)

class KpiMixin(models.AbstractModel):
    _name = "kpi.mixin"
    _description = "Mixin de Kpi"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    goal = fields.Float("Meta", tracking=True,)
    distributed_goal = fields.Float("Meta distribuida", tracking=True, compute="_compute_distributed_goal")
    progress = fields.Float("Progreso", compute="_compute_progress", tracking=True,)

    @api.constrains("goal", "distributed_goal",)
    def _check_goals(self):
        for rec in self:
            if round(rec.distributed_goal,2) > round(rec.goal,2):
                raise UserError(("La meta distribuida no puede ser mayor a la meta, DistributedGoal: %s, Goal: %s") % (rec.distributed_goal,rec.goal))