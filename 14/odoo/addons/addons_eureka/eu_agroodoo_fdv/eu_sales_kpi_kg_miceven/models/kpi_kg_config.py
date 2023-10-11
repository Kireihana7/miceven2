# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KpiKgConfig(models.Model):
    _inherit = 'kpi.kg.config'

    kpi_zone_ids = fields.One2many("kpi.config.zone", "kpi_kg_config_id", "Zonas", tracking=True,)
    zone_count = fields.Integer("Zonas", compute='_compute_zona_count', store=True)
    tipo_kpi = fields.Selection(string="Tipo de KPI",compute="_compute_tipo_kpi")

    @api.depends('company_id')
    def _compute_tipo_kpi(self):
        for rec in self:
            self.env['ir.config_parameter'] \
            .sudo() \
            .get_param('eu_sales_kpi_kg_miceven.tipo_kpi')
    
    #region Computes
    @api.depends("kpi_zone_ids.goal",'tipo_kpi')
    def _compute_distributed_goal(self):
        res = super()._compute_distributed_goal()
        for rec in self:
            if rec.tipo_kpi == 'zona':
                rec.distributed_goal = sum(rec.kpi_zone_ids.mapped("goal"))

    @api.depends("kpi_zone_ids.progress",'tipo_kpi')
    def _compute_progress(self):
        res = super()._compute_progress()
        for rec in self:
            if rec.tipo_kpi == 'zona':
                rec.progress = sum(rec.kpi_zone_ids.mapped("progress"))

    @api.depends("kpi_zone_ids",'tipo_kpi')            
    def _compute_zona_count(self):
        res = super()._compute_zona_count()
        for rec in self:
            if rec.tipo_kpi == 'zona':
                rec.zone_count = len(rec.kpi_zone_ids)

    #endregion

    #region Actions
    def action_compute_everything(self):
        salesperson = self.kpi_salesperson_id
        category = self.kpi_salesperson_category_id
        salesperson._compute_devoluciones()
        salesperson._compute_progress()
        category._compute_progress()
        category._compute_logro()
        category._compute_kpi_percent()
        
    def action_show_zone_ids(self):
        self.ensure_one()
        res = self.env.ref('eu_sales_kpi_kg_miceven.kpi_config_zone_action')
        res = res.read()[0]
        res['domain'] = str([('kpi_kg_config_id', '=', self.id)])
        res['context'] = {'create': False}
        return res
