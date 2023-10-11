# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    visit_ids = fields.One2many("res.visit", "partner_id", tracking=True,)
    last_visit_id = fields.Many2one(
        "res.visit", 
        "Última visita", 
        compute="_compute_last_visit", 
        tracking=True,
    )
    last_sale_order_id = fields.Many2one(
        "sale.order", 
        "Última orden de venta", 
        compute="_compute_last_sale_order", 
        tracking=True,
    )
    sale_amount_due = fields.Monetary("Total adeudado en ventas", compute="_compute_sale_amount_due")
    default_frequency_id = fields.Many2one("res.visit.frequency", "Frecuencia de visita")

    
    def computar_equipo_ventas(self):
        for rec in self.env['res.partner'].search([('user_id','!=',False)]):
            rec.team_id = rec.user_id.sale_team_id.id

    @api.onchange('user_id')
    def onchange_user_id_team(self):
        for rec in self:
            rec.team_id = rec.user_id.sale_team_id.id
    #region Computes
    @api.depends("invoice_ids.state", "invoice_ids.amount_residual", "invoice_ids.company_id")
    def _compute_sale_amount_due(self):
        for rec in self:
            rec.sale_amount_due = sum(
                rec.sudo()
                    .invoice_ids
                    .filtered(lambda x: all([
                        x.state =='posted',
                        x.amount_residual > 0,
                        x.move_type =='out_invoice',
                        x.company_id == self.env.company
                    ]))
                    .mapped("amount_residual")
            )
            
    @api.depends("sale_order_ids", "sale_order_ids.state", "sale_order_ids.date_order")
    def _compute_last_sale_order(self):
        for rec in self:
            if rec.sale_order_ids:
                order_ids = rec.sale_order_ids \
                    .filtered(lambda s: s.state in ("sale","done")) \
                    .sorted("date_order")
                
                rec.last_sale_order_id = order_ids[0] if order_ids else None
            else:
                rec.last_sale_order_id = None

    @api.depends("visit_ids", "visit_ids.fecha_visita")
    def _compute_last_visit(self):
        for rec in self:
            rec.last_visit_id = False
            if self.env.user.has_group('eu_sales_visit.sales_group_vendedor') or self.env.user.has_group('eu_sales_visit.sales_group_coordinador') or self.env.user.has_group('eu_sales_visit.sales_group_gerente_sucursal') or self.env.user.has_group('eu_sales_visit.sales_group_gerente_nacional'):
                if rec.visit_ids:
                    visit_ids = rec.visit_ids \
                        .filtered(lambda v: v.fecha_visita and (v.status in ["por_visitar", "visitando"])) \
                        .sorted("fecha_visita")

                    rec.last_visit_id = visit_ids[0] if visit_ids else None
    #endregion