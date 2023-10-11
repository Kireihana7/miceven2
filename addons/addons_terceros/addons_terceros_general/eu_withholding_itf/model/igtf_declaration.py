# coding: utf-8

from odoo import fields, models, api,_
from odoo.exceptions import UserError,Warning
from datetime import date

class IgtfDeclaration(models.Model):
    _name = 'igtf.declaration'
    _description = 'Declaración de IGTF'
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Descripción', readonly=True,
        default="/",
        help="Descripción de la declaración")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('declared', 'Declarada'),
        ('done', 'Pagada'),
        ('cancel', 'Cancelada'),
        ], string='Estado', readonly=True, default='draft',
        help="Estatus de la declaración")
    date_ini = fields.Date(
        string='Desde', readonly=True,
        required=True,
        default = fields.Date.context_today,
        states={'draft': [('readonly', False)]},
        help="Fecha Inicial de la declaración")
    date_fin = fields.Date(
        string='Hasta', readonly=True,
        required=True,
        default = fields.Date.context_today,
        states={'draft': [('readonly', False)]},
        help="Fecha Final de la declaración")
    journal_id = fields.Many2one('account.journal', string='Diario Pagador',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        domain="[('type','in',('bank','cash'))]")
    company_id = fields.Many2one(
        'res.company', string='Compañia', required=True, readonly=True,
        default=lambda self: self.env.company.id,
        help="Company")
    partner_id = fields.Many2one(
        'res.partner', string='Razón Social', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Entidad Gubernamental")
    product_id = fields.Many2one(
        'product.product', string='Producto', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Producto de Declaración",domain="[('type','=','service')]")
    amount_total = fields.Float(string='Total',
                                   readonly=True, compute='_compute_amount')
    amount_total_ref = fields.Float(string='Total Ref',
                                   readonly=True, compute='_compute_amount')
    lines = fields.One2many('igtf.declaration.line', 'move_id', 
                                    string='Líneas de IGTF', 
                                    readonly=True,
                                    copy=True,
                                    states={'draft': [('readonly', False)]},
                                    )
    
    move_paid_id = fields.Many2one('account.move', 
                            readonly=True, 
                            copy=False, 
                            string="Factura relacionada",help="Factura realizada de Pago",)
    payment_id = fields.Many2one('account.payment',string="Pago Declaración",copy=False,readonly=True)
    currency_id = fields.Many2one('res.currency',string="Moneda")
    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('igtf.declaration.seq')
        vals.update({
            'name': name
            })
        res = super(IgtfDeclaration, self).create(vals)
        return res   

    @api.depends('lines')
    def _compute_amount(self):
        for rec in self:
            rec.amount_total = sum(rec.lines.mapped('amount')) 
            rec.amount_total_ref = sum(rec.lines.mapped('amount_ref')) 
            
    @api.onchange('date_ini','date_fin')
    def onchange_dates(self):
        line_dict = {}
        for rec in self:
            if rec.date_ini and rec.date_fin:
                if rec.lines:
                    for lines in rec.lines:
                        values = [(5, 0, 0)]
                        rec.update({'lines': values})
                payments = [line for line in sorted(self.env['account.payment'].search([('is_igtf_declared','=',False),('is_igtf_payment', '=', True),('state', '=', 'posted'),('payment_type', '=', 'inbound'),('date', '>=', rec.date_ini),('date', '<=', rec.date_fin)]),
                    key=lambda x: x.partner_id.id)]
                for order in payments:
                    line_dict = {
                        'name':  order.id,
                        'journal_id': order.journal_id.id,
                        'date': order.date,
                        'partner_id': order.partner_id.id,
                        'amount': order.amount if order.currency_id == self.env.company.currency_id  else order.amount_ref,
                        'amount_ref': order.amount if order.currency_id != self.env.company.currency_id  else order.amount_ref,
                        'currency_id': order.currency_id.id,
                    }
                    lines = [(0,0,line_dict)]
                    rec.write({'lines':lines})


    def action_payment(self):
        return True

    def confirm_declaration(self):
        for rec in self:
            if len(rec.lines) == 0:
                raise UserError('Debes tener al menos un IGTF para Confirmar')
            rec.state = 'confirmed'
            for line in rec.lines:
                line.name.is_igtf_declared = True
                line.name.igtf_declaration = rec.id

    def action_declared(self):
        for rec in self:
            if len(rec.lines) == 0:
                raise UserError('Debes tener al menos un IGTF para Declarar')
            if not rec.move_paid_id and rec.journal_id and rec.product_id and rec.partner_id:
                monto = rec.amount_total_ref if rec.journal_id.currency_id else rec.amount_total
                rec.facturar(rec.journal_id,monto,rec.partner_id,rec.product_id)
            else:
                raise UserError('Falta información necesaria para la declaración')
            rec.state = 'declared'

    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            for line in rec.lines:
                line.name.is_igtf_declared = False
                line.name.igtf_declaration = False

    #Chequea que no se añadan dos Pagos Iguales
    @api.constrains('lines')
    def _check_exist_payment_in_line(self):
        for rec in self:
            exist_payment_list = []
            for line in rec.lines:
                if line.name.id in exist_payment_list:
                    raise ValidationError(_("No se puede añadir dos pagos iguales - %s") % (line.name.name)) 
                exist_payment_list.append(line.name.id)

    def create_invoice(self,currency_id,partner_id,journal_id):
        invoice_id = self.env["account.move"].create({
            "partner_id": partner_id.id,
            "partner_shipping_id": partner_id.id,
            "journal_id": self.env['account.move']
                .with_context(default_move_type='out_invoice')
                ._get_default_journal()
                .id,
            "currency_id": currency_id.id,
            "invoice_date": date.today(),
            "company_id": self.env.company,
            "move_type": 'out_invoice',
            "invoice_payment_term_id": False,
        })

        return invoice_id

    def create_lineas_vals(self, product_id,invoice_id,monto):
        return {
            'name': product_id.display_name,
            'product_id': product_id.id,
            'price_unit': monto,
            'move_id': invoice_id.id,
            'quantity':1,
            'product_uom_id':product_id.uom_id.id,
            "account_id": product_id.categ_id.property_account_income_categ_id.id,
        }

    def facturar(self,journal_id,monto,partner_id,product_id):
        currency_id = journal_id.currency_id if journal_id.currency_id else self.env.company.currency_id

        invoice_id = self.create_invoice(currency_id,partner_id,journal_id)

        vals = self.create_lineas_vals(product_id,invoice_id,monto)

        invoice_id.invoice_line_ids.with_context(check_move_validity=False).create(vals)
        invoice_id.with_context(check_move_validity=False)._onchange_partner_id()
        #invoice_id.invoice_line_ids._onchange_product_id()

        #for i, line in enumerate(invoice_id.invoice_line_ids):
        #    line.price_unit = self[i].amount * rate

        invoice_id._onchange_manual_currency_rate()
        invoice_id.invoice_line_ids._onchange_mark_recompute_taxes()
        invoice_id.invoice_line_ids._onchange_price_subtotal()
        invoice_id._onchange_invoice_line_ids()

        self.write({"move_paid_id": invoice_id.id})

class IgtfDeclarationLine(models.Model):
    _name = 'igtf.declaration.line'
    _description = 'Líneas de Declaración de IGTF'

    name = fields.Many2one('account.payment',string="IGTF",domain="[('is_igtf_payment','=',True)]")
    move_id = fields.Many2one('igtf.declaration',string="Declaración")
    journal_id = fields.Many2one(related="name.journal_id",string="Diario")
    date = fields.Date(related="name.date",string="Fecha")
    partner_id = fields.Many2one(related="name.partner_id",string="Cliente")
    amount = fields.Float(string="Monto",compute="_compute_amount",store=True)
    amount_ref = fields.Float(string="Monto Ref",compute="_compute_amount",store=True)
    currency_id = fields.Many2one(related="name.currency_id",string="Moneda")

    @api.depends('name')
    def _compute_amount(self):
        for rec in self:
            rec.amount = 0
            rec.amount_ref = 0
            if rec.name:
                rec.amount  = float(rec.name.amount) if rec.name.currency_id == self.env.company.currency_id  else float(rec.name.amount_ref)
                rec.amount_ref = float(rec.name.amount) if rec.name.currency_id != self.env.company.currency_id  else float(rec.name.amount_ref)
                