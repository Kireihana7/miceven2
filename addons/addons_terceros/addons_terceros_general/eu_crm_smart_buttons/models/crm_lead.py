# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, SUPERUSER_ID


class Lead(models.Model):
    _inherit = "crm.lead"

    count_sale_order = fields.Integer(compute='_compute_count_sale_order', string='Sale Order Count', readonly=True, store=False)
    total_invoiced = fields.Monetary(compute='_invoice_total', string="Total Invoiced", groups='account.group_account_invoice,account.group_account_readonly')
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True, string="Currency",)
    total_pagado = fields.Monetary(compute='_total_pagado', readonly=True, string="Total Pagado",)
    total_deuda = fields.Monetary(compute='_total_deuda', readonly=True, string="Vencidas",)
    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    
    @api.depends('partner_id')
    def _compute_count_sale_order(self):
        sales = self.env['sale.order'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.env.company.id),
            ('state', 'in', ('done','sale')),
            ])
        
        for rec in self:
            tot = 0
            for x in sales:
                tot += 1
            rec.count_sale_order = tot

    def action_view_sale_order(self):
        return False

    @api.depends('partner_id')
    def _total_deuda(self):

        account = self.env['account.move'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ("not_paid","partial")),
            ('invoice_date_due', '<', fields.Date.today()),
            ('company_id', '=', self.env.company.id),
            ])
        
        self.total_deuda = 0
        for rec in self:
            cont = 0
            if rec.partner_id:
                for x in account:
                    cont += x.amount_total
                rec.total_deuda = cont

    @api.depends('partner_id')
    def _invoice_total(self):
        self.total_invoiced = 0

        account = self.env['account.move'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('company_id', '=', self.env.company.id),
            ('state', '!=', 'cancel'),
            ])
        for rec in self:
            cont = 0
            if rec.partner_id:
                for x in account:
                    cont += x.amount_total
                rec.total_invoiced = cont

    def _get_company_currency(self):
        for partner in self:
            if partner.company_id:
                partner.currency_id = partner.sudo().company_id.currency_id
            else:
                partner.currency_id = self.env.company.currency_id

    @api.depends('partner_id')
    def _total_pagado(self):
        payment = self.env['account.payment'].sudo().search([
            ('partner_id', '=', self.partner_id.id), 
            ('payment_type', '=', 'inbound'), 
            ('company_id', '=', self.env.company.id)])
        
        for rec in self:
            tot = 0            
            for x in payment:
                tot += x.amount
            rec.total_pagado = tot

    @api.depends('partner_id')
    def _compute_meeting_count(self):
        if self.ids:
            meeting_data = self.env['calendar.event'].sudo().read_group([
                ('opportunity_id', 'in', self.ids)
            ], ['opportunity_id'], ['opportunity_id'])
            mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        else:
            mapped_data = dict()
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)
    
    def action_view_partner_invoices(self):
        return False

    def total_pagado_button(self):
        return False

    def total_deuda_button(self):
        return False

    def sale_order_count_button(self):
        return False