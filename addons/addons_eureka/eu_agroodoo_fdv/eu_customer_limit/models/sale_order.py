# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    tiene_deuda = fields.Boolean(string="Tiene Deuda Pendiente", compute="_compute_tiene_deuda")
    monto_deuda_total = fields.Float(string="Monto Deuda Total")
    corporativo = fields.Boolean(related="partner_id.corporativo")
    ultima_factura = fields.Date(string="Fecha de Ult. Fact.", compute="_compute_tiene_deuda", store=True)
    monto_adeudado_ultima_factura = fields.Float(string="Monto Deuda Ult. Fact.", compute="_compute_tiene_deuda", store=True)
    balance_cliente = fields.Float(string="Balance del Cliente",compute="_compute_balance_cliente")
    estatus_balance = fields.Char(string="Estatus Balance",compute="_compute_balance_cliente")
    # UPDATE:
    oldest_due_date = fields.Date(string="Fecha más vieja", compute="_compute_oldest_due_date")
    oldest_due_days = fields.Integer(string="Días transcurridos", compute="_compute_oldest_due_date")

    def button_balance_pass(self):
        pass
    def button_balance_notpass(self):
        pass
        
    @api.depends('partner_id')
    def _compute_oldest_due_date(self):
        for rec in self:
            rec.oldest_due_date = False
            rec.oldest_due_days = 0
            if rec.partner_id:
                query_oldest_due_date = """
                    SELECT invoice_date_due
                    FROM account_move
                    WHERE partner_id = %s
                        AND move_type = 'out_invoice'
                        AND state = 'posted'
                        AND amount_residual > 0
                        AND invoice_date_due < CURRENT_DATE
                    ORDER BY invoice_date_due
                    LIMIT 1
                """
                self.env.cr.execute(query_oldest_due_date, (rec.partner_id.id if rec.partner_id else 0,))
                result_oldest_due_date = self.env.cr.fetchone()

                if result_oldest_due_date and result_oldest_due_date[0]:
                    rec.oldest_due_date = result_oldest_due_date[0]
                    current_date = fields.Date.today()
                    diferencia = current_date - rec.oldest_due_date
                    rec.oldest_due_days = diferencia.days

    @api.depends('partner_id')
    def _compute_balance_cliente(self):
        for rec in self:
            query = """
                SELECT
                    SUM(balance) AS total_balance
                FROM
                    account_move_line aml
                INNER JOIN
                    account_account aa ON aa.id = aml.account_id
                WHERE
                    aml.parent_state = 'posted'
                    AND aa.user_type_id = (
                        SELECT id
                        FROM account_account_type
                        WHERE type = 'receivable'
                    )
                    AND partner_id = %s
            """
            self.env.cr.execute(query, (rec.partner_id.id if rec.partner_id else 0,))
            result = self.env.cr.fetchone()
            monto = 0
            rec.balance_cliente = 0
            rec.estatus_balance = 'cero'
            if result and result[0]:
                monto = float(result[0])
                rec.balance_cliente = abs(monto) 
                if monto > 0.0000:
                    rec.estatus_balance = 'deuda' 
                if monto < 0.0000:
                    rec.estatus_balance = 'favor'

    @api.depends('partner_id', 'company_id')
    def _compute_tiene_deuda(self):
        for rec in self:
            rec.tiene_deuda = False
            rec.monto_deuda_total = 0
            domain = [
                ('amount_residual', '>', 0),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('company_id', '=', rec.company_id.id),
                ('invoice_date_due', '<', date.today())
            ]
            if rec.partner_id.parent_id:
                domain.append(('partner_id', 'child_of', rec.partner_id.parent_id.id))
            else:
                domain.append(('partner_id', 'child_of', rec.partner_id.id))
            ventas = sum(self.env['account.move'].sudo().search(domain).mapped('amount_residual'))
            if ventas > rec.company_id.maximo_deuda_permitida:
                rec.tiene_deuda = True
                rec.monto_deuda_total = round(ventas, 2)
            query = """
                SELECT invoice_date, amount_residual
                FROM account_move
                WHERE state = 'posted'
                    AND company_id = %s
                    AND move_type = 'out_invoice'
                    AND partner_id = %s
                ORDER BY invoice_date ASC
                LIMIT 1
            """
            self.env.cr.execute(query, (rec.company_id.id if rec.company_id else 0, rec.partner_id.id if rec.partner_id else 0))
            result = self.env.cr.fetchone()
            if result:
                rec.ultima_factura = result[0]
                rec.monto_adeudado_ultima_factura = round(result[1], 2)

    def action_confirm(self):
        for order in self:
            if order.tiene_deuda and not order.corporativo:
                raise UserError(('¡Este Contacto tiene deuda de %s, no se puede confirmar esta venta!')% (round(order.monto_deuda_total,2)))
        return super(SaleOrder, self).action_confirm()
