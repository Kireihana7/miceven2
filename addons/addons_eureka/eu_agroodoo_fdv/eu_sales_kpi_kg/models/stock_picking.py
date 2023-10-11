# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time, datetime
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    visit_id = fields.Many2one("res.visit", "Visita", related= "sale_id.visit_id", tracking=True)

    
    def button_validate(self):
        vals= super().button_validate()
        if self.visit_id:
            self.env['res.traceability'].sudo().search([('sale_visii', '=', self.visit_id.id)]).sudo().write({'date_done_stock': datetime.datetime.today()})
      
        return vals   



