# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("commission_id",'amount_untaxed','amount_total')
    def _compute_commission_total(self):
        for rec in self:
            rec.commission_total = 0
            rec.commission_percent = 0
            if rec.commission_id and rec.commission_id.amount_base_type == 'base_imponible':
                rec.commission_total,rec.commission_percent =  rec.commission_id.calculate_section(rec.amount_untaxed)
            elif rec.commission_id and rec.commission_id.amount_base_type == 'monto_total':
                rec.commission_total,rec.commission_percent = rec.commission_id.calculate_section(rec.amount_total)

    commission_total = fields.Float(
        string="Monto Comisión",
        compute="_compute_commission_total",
        store=True,
        copy=False,
    )
    commission_percent = fields.Float(
        string="Porcentaje Comisión",
        compute="_compute_commission_total",
        store=True,
        copy=False)

    comission_partner = fields.Many2one(
        string="Comisionista",
        comodel_name="res.partner",
        compute="_compute_comission_partner",
        copy=False,
    )

    @api.depends("user_id")
    def _compute_comission_partner(self):
        for rec in self:
            rec.comission_partner = self.env['res.partner'].search([('user_comission','=',rec.user_id.id)],limit=1).id or False

    @api.depends("comission_partner","company_id","user_id")
    def _compute_commission_id(self):
        for rec in self:
            commission_id = self.env['sale.commission'].search([
                ('partner_id','=',rec.comission_partner.id),
                ('company_id','=',rec.company_id.id),
                ('state','=','active'),
                ('ejecutar','=','sale'),
                ],limit=1).id
            rec.commission_id  = commission_id

    commission_id = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        compute="_compute_commission_id",
        store=True,
        readonly=True,
        copy=False,
        string="Comisión",
    )
    commission_id_line = fields.Many2one(
        comodel_name="sale.commission.line",
        readonly=True,
        copy=False,
        string="Línea de Comisión",
    )

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            if rec.commission_id and rec.commission_id.state != 'active' and not rec.commission_id_line:
                rec._compute_commission_id()
                rec._compute_commission_total()
            if rec.commission_id and rec.commission_id.state == 'active' and not rec.commission_id_line:
                data = {
                    'commission_id': rec.commission_id.id,
                    'name': '%s - %s' % (rec.name,rec.partner_id.name) ,
                    'sale_id': rec.id,
                    'invoice_id': False,
                    'partner_id': rec.partner_id.id,
                    'amount_total': rec.commission_total,
                    'amount_to_paid': rec.commission_total,
                    'amount_paid': 0,
                    'payment_state': 'not_paid',
                }
                lines = self.env['sale.commission.line'].sudo().create(data)
                rec.commission_id_line = lines.id
        return res

    def write(self,vals):
        for rec in self:
            if vals.get('state') not in ('confirm','sale') and rec.commission_id_line and rec.commission_id_line.amount_total != rec.commission_id_line.amount_to_paid:
                raise UserError('No puedes modificar una Venta que tenga una comision pagada')
        res = super(SaleOrder, self).write(vals)
        for rec in self:
            if rec.commission_id_line and (rec.commission_id_line.amount_total == rec.commission_id_line.amount_to_paid or rec.commission_id_line.payment_state != 'not_paid'):
                data = {
                    'commission_id': rec.commission_id.id,
                    'name': '%s - %s' % (rec.name,rec.partner_id.name) ,
                    'sale_id': rec.id,
                    'invoice_id': False,
                    'partner_id': rec.partner_id.id,
                    'amount_total': rec.commission_total,
                    'amount_to_paid': rec.commission_total,
                    'amount_paid': 0,
                    'payment_state': 'not_paid',
                }
                rec.commission_id_line.sudo().write(data)
            if rec.commission_id_line and (rec.commission_id_line.amount_total != rec.commission_id_line.amount_to_paid or rec.commission_id_line.payment_state != 'not_paid') and rec.commission_id_line.amount_total != rec.commission_total:
                raise UserError('No puedes modificar el monto de una venta que ya tenga comisión pagada')
        return res
