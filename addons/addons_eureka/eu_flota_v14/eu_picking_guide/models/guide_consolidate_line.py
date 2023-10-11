# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class GuideConsolidateLine(models.Model):
    _name = 'guide.consolidate.line'
    _description ="Picking Guide Line"

    name = fields.Char(string="Nombre de la Línea")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    guide_consolidate_id_line = fields.Many2one(
        'guide.consolidate',
        string='Picking Guide', 
    )

    picking_id = fields.Many2one(
        'stock.picking',
        string='Pickings',
        required=True,
        domain="[('picking_type_id.code', '=', 'outgoing'),('state', '=', 'done'),('dispatch_status', '=', 'no_dispatch'),('company_id', '=', company_id)]",
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        readonly=True,
        store=True,
    )
    total_items = fields.Float(
        string="Total Items",
        compute="_compute_total_su",
        store=True,
    )
    zona = fields.Many2one(
        'partner.zone',
        string="Zone",
        readonly=True,
        store=True,
    )
    invoice_rel = fields.Many2one('account.move',string="Factura Asociada",store=True)
    #Traer Cliente de la SU
    @api.onchange('picking_id')
    def onchange_product_id(self):
        for rec in self:
            rec.partner_id = rec.picking_id.partner_id.id
            rec.invoice_rel = self.env['account.move'].search([('name','=',rec.picking_id.invoice_rel)],limit=1).id
            rec.zona       = rec.picking_id.partner_id.zone.id
    
    # Computar Total de Items en SU
    @api.depends('picking_id')
    def _compute_total_su(self):
        for rec in self:
            rec.total_items = 0.0
            for su in rec.picking_id.move_ids_without_package:
                rec.total_items = rec.total_items + su.quantity_done
            for picking in rec.picking_id:
                if rec.guide_consolidate_id_line.state == 'waiting':
                    picking.dispatch_status = 'to_dispatch'
                if rec.guide_consolidate_id_line.state == 'draft':
                    picking.dispatch_status = 'no_dispatch'
    # Evita dejar un Picking en por Despachar si se elimina de la Guía de despacho estando en To dispatch    
    def unlink(self):
        for rec in self:
            if rec.picking_id:
                for picking in rec.picking_id:
                    if picking.dispatch_status != 'dispatched':
                        picking.dispatch_status = 'no_dispatch'
        return super(GuideConsolidateLine, self).unlink()
    

