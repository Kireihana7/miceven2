# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import UserError
from odoo.tests.common import Form

class SaleCommissionPayment(models.Model):
    _name="sale.commission.payment"
    _description = "Concepto de Cancelación Romana"

    name = fields.Char(string="Ref Pago",default="/")
    sale_commission_line = fields.Many2one("sale.commission.line",string="Línea de Comisión", required =True,readonly=True)
    commission_id = fields.Many2one("sale.commission",string="Línea de Comisión", required =True,related="sale_commission_line.commission_id",readonly=True,store=True)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always')
    journal_id = fields.Many2one('account.journal',string="Diario",required =True,domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]")
    comercial = fields.Many2one(string="Comercial",readonly=True,required=True,related="sale_commission_line.comercial",store=True)
    sale_id = fields.Many2one('sale.order',string="Venta Asociada",readonly=True,related="sale_commission_line.sale_id",store=True)
    invoice_id = fields.Many2one('account.move',string="Factura Asociada",readonly=True,related="sale_commission_line.invoice_id",store=True)
    partner_id = fields.Many2one('res.partner',string="Contacto",readonly=True,related="sale_commission_line.partner_id",store=True)
    amount_total = fields.Float(string="Monto Total de Comisiones",readonly=True,defalt=0,related="sale_commission_line.amount_total",store=True)
    amount_to_paid = fields.Float(string="Monto por Pagar",readonly=True,defalt=0,related="sale_commission_line.amount_to_paid",store=True)
    amount_paid = fields.Float(string="Monto Pagado",readonly=True,defalt=0,related="sale_commission_line.amount_paid",store=True)
    amount = fields.Float(string="Monto",default=0)
    payment_id = fields.One2many(comodel_name="account.move",inverse_name="commission_payment_id_payment", string="Pagos",readonly=True)
    product_id = fields.Many2one(string="Producto a Facturar", comodel_name="product.product", required=True,domain="[('type', '=', 'service')]")
    payment_count = fields.Integer(string="Cantidad de Pagos",compute="_compute_payment_count")
    state = fields.Selection(selection=[('cancel','Cancelada'),('done','Hecho')],string="Estatus",readonly=True,default='cancel')
    nota_credito = fields.Boolean(string="Nota de Crédito",default=False)
    
    @api.depends('payment_id')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_id)

    def show_payments(self):
        self.ensure_one()
        res = self.env.ref('account.action_move_in_invoice_type')
        res = res.read()[0]
        res['context'] = {'create':False}
        res['domain'] = str([('commission_payment_id_payment', '=', self.id)])
        return res

    def action_pagar_comision(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Pagar Comisión'),
            'res_model': 'sale.commission.payment',
            'view_mode': 'form',
            'view_id': len(active_ids) != 1 and self.env.ref('eu_sale_comission_total.view_sale_commission_payment_form_wizard').id or self.env.ref('eu_sale_comission_total.view_sale_commission_payment_form_wizard').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('sale.commision.payment.seq')
        vals.update({
            'name': name
            })
        res = super(SaleCommissionPayment, self).create(vals)
        return res   

    def create_payment(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError('El monto a pagar debe ser mayor a cero')
            if rec.amount > rec.amount_to_paid and not rec.nota_credito:
                raise UserError('No puedes pagar más de lo que está por pagar.')
            if rec.amount > rec.amount_paid and rec.nota_credito:
                raise UserError('No puedes devolver más de lo pagado')
            product_account = rec.product_id.categ_id.property_account_expense_categ_id.id
            partner_account = rec.comercial.property_account_payable_id.id
            ref_payment = str(rec.sale_id.name) + str(rec.comercial.name) + str(rec.id)
            invoices = rec.make_invoices(rec.journal_id.id, rec.product_id.id,rec.comercial.id,rec.amount,rec.commission_id.id,rec.sale_commission_line.id,rec.id,product_account,partner_account,ref_payment,rec.nota_credito)
            if not rec.nota_credito:
                state_line = 'paid' if rec.amount_to_paid-rec.amount == 0 else 'partial_payment'
                rec.sale_commission_line.write({'amount_to_paid':rec.amount_to_paid-rec.amount,'amount_paid':rec.amount_paid+rec.amount,'payment_state':state_line})
            else:
                state_line = 'not_paid' if rec.amount_to_paid - rec.amount_total == 0 else 'partial_payment'
                rec.sale_commission_line.write({'amount_to_paid':rec.amount_to_paid+rec.amount,'amount_paid':rec.amount_paid-rec.amount,'payment_state':state_line})
            rec.state = 'done'
            if len(invoices):
                return {
                    "name": _("Facturas Creadas"),
                    "type": "ir.actions.act_window",
                    "views": [[False, "list"], [False, "form"]],
                    "res_model": "account.move",
                    "domain": [["id", "in", invoices.ids]],
                    "context": {'create':False},
                }

    @api.constrains('amount')
    def _constrains_amount(self):
        for rec in self:
            if rec.amount == 0:
                raise UserError('El monto a pagar debe ser mayor a cero')
    @api.model
    def default_get(self, default_fields):
        rec = super(SaleCommissionPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'sale.commission.line':
            return rec
        sale_commission_line = self.env['sale.commission.line'].browse(active_ids)
        if not sale_commission_line:
            raise UserError(_("Debe tener una Línea de comisión para poder pagar"))
        rec.update({
            'sale_commission_line': sale_commission_line[0].id,
        })
        return rec

    def _prepare_invoice(self, journal, product,comercial,amount,commission_id,sale_comission_line,id_comi,product_account,partner_account,ref_payment,nota_credito):
        self.ensure_one()
        vals = {
            'date': fields.Datetime.now(),
            'journal_id': journal,
            'line_ids': False,
            'state': 'draft',
            'partner_id': comercial,
            'move_type':'in_invoice' if not nota_credito else 'in_refund',
            'commission_payment_id': commission_id,
            'commission_payment_id_line': sale_comission_line,
            'commission_payment_id_payment': id_comi,
        }
        move_apply_id = self.env['account.move'].sudo().create(vals)
        move_advance = {
            'account_id': product_account,
            'product_id': product,
            'company_id': self.env.company.id,
            'currency_id': False,
            'date_maturity': False,
            'ref': ref_payment,
            'date': fields.Datetime.now(),
            'partner_id': comercial,
            'move_id': move_apply_id.id,
            'name': 'Pago de Comisiones' if not nota_credito else 'Devolución de Comisiones',
            'journal_id': journal,
            'debit': amount if not nota_credito else 0.0,
            'credit': amount if nota_credito else 0,
        }
        asiento = move_advance
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.with_context(check_move_validity=False).create(asiento)
        move_apply_id.with_context(check_move_validity=False)._onchange_partner_id()
        move_apply_id.with_context(check_move_validity=False).action_post()
        return move_apply_id

    def make_invoices(self, journal, product,comercial,amount,commission_id,sale_commission_line,id_comi,product_account,partner_account,ref_payment,nota_credito):
        invoice_vals_list = []
        for rec in self:
            invoice_vals = rec._prepare_invoice(journal, product,comercial,amount,commission_id,sale_commission_line,id_comi,product_account,partner_account,ref_payment,nota_credito)
        return invoice_vals

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError('No se puede eliminar un Pago realizado')
        res = super(SaleCommissionPayment, self).unlink()
        return res