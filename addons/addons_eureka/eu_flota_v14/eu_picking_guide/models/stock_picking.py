# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dispatch_status = fields.Selection([
        ('no_dispatch', 'No Dispatch'),
        ('to_dispatch', 'To Dispatch'),
        ('dispatched', 'Dispatched'),
        ('cancel', 'Undispatched'),
        ], string='Dispatch Status', readonly=True, copy=False, index=True, track_visibility='always', default='no_dispatch')

    fleet                   = fields.Many2one("fleet.vehicle", string="Vehicle")
    driver_id               = fields.Many2one("res.partner", "Driver", related="fleet.driver_id")
    license_plate           = fields.Char(string="License plate", related="fleet.license_plate")
    invoice_rel             = fields.Char(related="sale_id.invoice_ids.name",string="Factura Relacionada")
    sale_rel                = fields.Char(related="sale_id.name",string="SO Relacionada")
    invoice_rel_status      = fields.Selection(related="sale_id.invoice_ids.state",string="Estado Factura Relacionada")
    sale_rel_status         = fields.Selection(related="sale_id.state",string="Estado SO Relacionada")
    guide_consolidate       = fields.Many2one('guide.consolidate', string="Picking Guide", compute="_compute_guide")
    # Pasar a No Despachable
    def button_undispatched(self):
        for rec in self:
            rec.dispatch_status = 'cancel'

    # Pasar a Permitir Despacho
    def button_dispatched(self):
        for rec in self:
            rec.dispatch_status = 'no_dispatch'
    # Automaticamente pasa a No despachable los Pickings cancelados
    def action_cancel(self):
        for rec in self:
            rec.dispatch_status = 'cancel'
        return super(StockPicking, self).action_cancel()

    def _compute_guide(self):
        for rec in self:
            rec.guide_consolidate = False
            for line in rec.env['guide.consolidate.line'].search([('guide_consolidate_id_line', '!=', False),('picking_id', '=', rec.id)],limit=1):
                rec.guide_consolidate = line.guide_consolidate_id_line.id