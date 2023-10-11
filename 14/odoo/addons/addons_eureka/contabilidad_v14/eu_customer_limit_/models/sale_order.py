# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    company_currency_id = fields.Many2one('res.currency',string="Moneda de la Compañía",related="company_id.currency_id")
    tiene_deuda = fields.Boolean(string="Tiene Deuda Pendiente",compute="_compute_tiene_deuda")
    monto_deuda_total = fields.Float(string="Monto Deuda Total")
    corporativo = fields.Boolean(related="partner_id.corporativo")
    
    @api.depends('partner_id','company_id')
    def _compute_tiene_deuda(self):
        for rec in self:
            rec.tiene_deuda = False
            rec.monto_deuda_total = 0
            domain = [
                ('corporativo','=',False),
                ('amount_residual','>',0),
                ('state','=','posted'),
                ('move_type','=','out_invoice'),
                ('company_id','=',rec.company_id.id),
                ('invoice_date_due','<',date.today())
            ]
            if rec.partner_id.parent_id:
                domain.append(('partner_id','child_of', rec.partner_id.parent_id.id))
            else:
                domain.append(('partner_id','child_of', rec.partner_id.id))
            ventas = sum(self.env['account.move'].sudo().search(domain).mapped('amount_residual'))
            if ventas > rec.company_id.maximo_deuda_permitida:
                rec.tiene_deuda = True
                rec.monto_deuda_total = round(ventas,2)

    # def action_confirm(self):
    #     for order in self:
    #         if order.tiene_deuda:
    #             raise UserError(('¡Este Contacto tiene deuda de %s, no se puede confirmar esta venta!')% (round(order.monto_deuda_total,2)))
    #     return super(SaleOrder, self).action_confirm()

    def open_current_invoice_residual(self):
        self.ensure_one()
        account_obj = self.env['account.move'].sudo()
        domain_vc = [
                ('corporativo','=',False),
                ('amount_residual','>',0),
                ('state','=','posted'),
                ('move_type','=','out_invoice'),
                ('company_id','=',self.company_id.id),
                ('invoice_date_due','<=',date.today()),
                ('invoice_user_id','=',self.env.user.id),
            ]
        if self.partner_id.parent_id:
            domain_vc.append(('partner_id','child_of', self.partner_id.parent_id.id))
        else:
            domain_vc.append(('partner_id','child_of', self.partner_id.id))
        facturas = account_obj.search(domain_vc)
        if len(account_obj.search(domain_vc))==0:
            raise UserError('No existen facturas por pagar de este cliente')
        res = self.env.ref('account.action_move_out_invoice_type')
        res = res.read()[0]
        res['domain'] = str([('id', 'in', facturas.mapped('id'))])
        res['context'] = {'delete':False,'create':False,'edit':False,'duplicate':False}
        return res