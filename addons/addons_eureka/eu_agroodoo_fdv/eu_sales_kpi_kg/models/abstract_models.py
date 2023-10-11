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
    distributed_goal = fields.Float(
        "Meta distribuida",
        compute="_compute_distributed_goal",
        tracking=True, 
        store=True,
    )
    progress = fields.Float(
        "Progreso",
        compute="_compute_progress",
        tracking=True,
        store=True,
    )
    progress_percent = fields.Float(
        "Progreso %",
        compute="_compute_progress_percent", 
        tracking=True,
        store=True,
    )

    @api.depends('progress','goal')
    def _compute_progress_percent(self):
        for rec in self:
            rec.progress_percent = 0

            if rec.progress != 0 and rec.goal != 0:
                rec.progress_percent = round((rec.progress * 100) / rec.goal, 2)

    @api.constrains("goal", "distributed_goal",)
    def _check_goals(self):
        for rec in self:
            if round(rec.distributed_goal, 2) > round(rec.goal, 2):
                raise UserError(("La meta distribuida no puede ser mayor a la meta, DistributedGoal: %s, Goal: %s") % (rec.distributed_goal, rec.goal))