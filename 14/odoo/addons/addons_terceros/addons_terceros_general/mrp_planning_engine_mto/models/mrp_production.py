# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductionOrder(models.Model):
    _inherit = 'mrp.production'


    def action_confirm(self):
        res = super().action_confirm()
        for production in self:
            if production.mto_origin:
                sale_id = self.env["sale.order"].search([("name", "=", production.mto_origin)])
                if sale_id and sale_id.analytic_account_id:
                    production.analytic_account_id = sale_id.analytic_account_id
                    moves = (production.mapped('move_raw_ids') + production.mapped('move_finished_ids')).filtered(lambda r: r.state not in ['done', 'cancel'])
                    moves.write({'analytic_account_id': production.analytic_account_id})
        return res

    def button_mark_done(self):
        for production in self:
            moves = (production.mapped('move_raw_ids') + production.mapped('move_finished_ids')).filtered(lambda r: r.state not in ['done', 'cancel'])
            moves.write({'analytic_account_id': production.analytic_account_id.id})
        return super().button_mark_done()
