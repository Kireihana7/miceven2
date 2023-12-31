# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api,_

class ShPurchase(models.Model):
    _inherit='purchase.order'
    
    agreement_id = fields.Many2one('purchase.agreement','Purchase Tender')
    cancel_lines = fields.Boolean("Cancel Lines",compute='get_cancel_lines',store=True)
    selected_order = fields.Boolean("Selected Orders")
    sh_msg = fields.Char("Message",compute='_compute_sh_msg')
    incluye_flete = fields.Boolean("Incluye Flete")

    @api.depends('partner_id')
    def _compute_sh_msg(self):
        if self:
            for rec in self:
                rec.sh_msg = ''
                if rec.agreement_id and rec.partner_id.id not in rec.agreement_id.partner_ids.ids:
                    rec.sh_msg = 'El proveedor que ha seleccionado no existe en la oferta seleccionada. Todavía puede crear una cotización para el seleccionado.'
    
    
    def get_cancel_lines(self):
        if self:
            for rec in self:
                if rec.state=='cancel':
                    rec.cancel_lines = True 
                else:
                    rec.cancel_lines = False

class ShPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'
    
    status = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],string="State",default='draft')
    agreement_id = fields.Many2one('purchase.agreement','Purchase Tender',related='order_id.agreement_id',store=True)
    cancel_lines = fields.Boolean("Cancel Lines",related='order_id.cancel_lines',store=True)
    incluye_flete = fields.Boolean("Incluye Flete",related="order_id.incluye_flete",store=True)
    payment_term_id = fields.Many2one(related="order_id.payment_term_id",string="Plazos de Pago")
    
    def action_confirm(self):
        if self:
            for rec in self:
                rec.status = 'confirm'
                
    def action_cancel(self):
        if self:
            for rec in self:
                rec.status = 'cancel'
    
    def action_update_qty(self):
        if self:
            return {
                'name': _('Change Quantity'),
                'type': 'ir.actions.act_window',
                'res_model': 'update.qty',
                'view_type':'form',
                'view_mode': 'form',
                'target':'new'
                }