# -*- coding: utf-8 -*-
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError,ValidationError

class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Commission in sales"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=False, readonly=True,default="/")
    section_ids = fields.One2many(
        string="Sections",
        comodel_name="sale.commission.section",
        inverse_name="commission_id",
    )
    state = fields.Selection(selection=[
        ('cancel','Cancelada'),
        ('draft','Borrador'),
        ('active','Activa'),
    ],string="Estatus",readonly=True,default='draft')
    amount_base_type = fields.Selection(
        selection=[
            ("base_imponible", "Base Imponible"), 
            ("monto_total", "Monto Total")
        ],
        string="Basado en",
        required=True,
        default="base_imponible",
    )
    partner_id = fields.Many2one('res.partner',string="Comercial",required=True,domain=[('user_comission','!=',False)])
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always')
    ejecutar = fields.Selection(selection=[
        ('sale','Ventas'),
        ('invoice','Facturas'),
    ],string="Ejecutar en", required=True,default="sale")
    sale_ids = fields.One2many(comodel_name="sale.order",inverse_name="commission_id",string="Ventas Vinculadas",readonly=True)
    invoice_ids = fields.One2many(comodel_name="account.move",inverse_name="commission_id",string="Facturas Vinculadas",readonly=True)
    line_ids = fields.One2many(comodel_name="sale.commission.line",inverse_name="commission_id",string="Líneas de Comisiones",readonly=True)

    amount_total = fields.Float(string="Monto Total de Comisiones",compute="_compute_totales")
    amount_to_paid = fields.Float(string="Monto por Pagar",compute="_compute_totales")
    amount_paid = fields.Float(string="Monto Pagado",compute="_compute_totales")

    payment_ids = fields.One2many(comodel_name="account.move",inverse_name="commission_payment_id",string="Pagos Asociados")

    @api.depends('line_ids')
    def _compute_totales(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('amount_total'))
            rec.amount_to_paid = sum(rec.line_ids.mapped('amount_to_paid'))
            rec.amount_paid = sum(rec.line_ids.mapped('amount_paid'))


    def calculate_section(self, base):
        self.ensure_one()
        for section in self.section_ids:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0, section.percent
        return 0.0,0.0

    def button_confirm(self):
        for rec in self:
            if len(self.env['sale.commission'].search([
                ('partner_id','=',rec.partner_id.id),
                ('state','=','active'),
                ('id','!=',rec.id),
                ('company_id', '=',rec.company_id.id)
                ]))>0:
                raise UserError('Un comercial no puede tener dos Comisiones activas a la vez')
            else:
                rec.state = 'active'

    def button_cancel(self):
        for rec in self:
            if rec.ejecutar == 'venta':
                rec.sale_ids.filtered(lambda x: x.state not in ('confirm','sale')).write({'commission_id':False,'comission_partner':False})
            if rec.ejecutar == 'invoice':
                rec.invoice_ids.filtered(lambda x: x.state =='posted').write({'commission_id':False,'comission_partner':False})
            rec.state = 'cancel'

    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('sale.commision.seq')
        vals.update({
            'name': name
            })
        res = super(SaleCommission, self).create(vals)
        return res   

    def unlink(self):
        for rec in self:
            if len(rec.sale_ids)>0 or len(rec.invoice_ids)>0:
                raise UserError('No puedes eliminar una Comisiión con Ventas o Facturas Vinculadas')
        return super(SaleCommission, self).unlink()

class SaleCommissionSection(models.Model):
    _name = "sale.commission.section"
    _description = "Commission section"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    commission_id = fields.Many2one("sale.commission", string="Commission")
    amount_from = fields.Float(string="Desde")
    amount_to = fields.Float(string="Hasta")
    percent = fields.Float(string="Porcentaje", required=True)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, related="commission_id.company_id")
    @api.constrains("amount_from", "amount_to")
    def _check_amounts(self):
        for section in self:
            if section.amount_to < section.amount_from:
                raise ValidationError(
                    _("The lower limit cannot be greater than upper one.")
                )

class SaleCommissionLine(models.Model):
    _name = "sale.commission.line"
    _description = "Commission Line"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",readonly=True,required=True)
    commission_id = fields.Many2one("sale.commission", string="Commission",readonly=True,required=True)
    comercial = fields.Many2one("res.partner",related="commission_id.partner_id", string="Comisionista",readonly=True,required=True)
    sale_id = fields.Many2one('sale.order',string="Venta Asociada",readonly=True)
    invoice_id = fields.Many2one('account.move',string="Factura Asociada",readonly=True)
    partner_id = fields.Many2one('res.partner',string="Contacto",readonly=True)
    amount_total = fields.Float(string="Monto Total de Comisiones",readonly=True,defalt=0,required=True)
    amount_to_paid = fields.Float(string="Monto por Pagar",readonly=True,defalt=0,required=True)
    amount_paid = fields.Float(string="Monto Pagado",readonly=True,defalt=0,required=True)
    payment_state = fields.Selection(selection=[
        ('not_paid','No pagada'),
        ('partial_payment','Pagada Parcialmente'),
        ('paid','Pagada'),
    ],string="Estatus del Pago",readonly=True,default='not_paid')
    company_id = fields.Many2one('res.company',string="Compañía", required=True, related="commission_id.company_id")
    payment_ids = fields.One2many(comodel_name="sale.commission.payment",inverse_name="sale_commission_line",string="Pagos Asociados")
   
    def button_payment(self):
        return self.env['sale.commission.payment']\
            .with_context(active_ids=self.ids, active_model='sale.commission.line', active_id=self.id)\
            .action_pagar_comision()

class SaleCommissionFullPayment(models.Model):
    _name = "sale.commission.full"
    _description = "Commission Payment Full"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",readonly=True,required=True,default='/')
    line_ids = fields.One2many(comodel_name="sale.commission.full.line",inverse_name="full_id",string="Líneas asociadas")
    invoice_ids = fields.One2many(comodel_name="account.move",inverse_name="commission_id_full",string="Pagos Asociados")
    state = fields.Selection(selection=[
        ('cancel','Cancelada'),
        ('draft','Borrador'),
        ('done','Hecho'),
    ],string="Estatus",readonly=True,default='draft')
    monto_total = fields.Float(string="Monto total",compute="_compute_monto_total")
    product_id = fields.Many2one(string="Producto a Facturar", comodel_name="product.product", required=True,domain="[('type', '=', 'service')]")
    journal_id = fields.Many2one('account.journal',string="Diario",required =True,domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]")
    payment_count = fields.Integer(string="Cantidad de Pagos",compute="_compute_payment_count")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always')

    @api.depends('line_ids')
    def _compute_monto_total(self):
        for rec in self:
            rec.monto_total = sum(rec.line_ids.mapped('amount_total'))

    def button_confirm(self):
        for rec in self:
            if len(rec.line_ids) == 0:
                raise UserError('Debes añadir al menos una línea de comisión')
            if len(rec.line_ids.commission_line_id.filtered(lambda line: line.amount_paid != 0))> 0:
                raise UserError('Todas las líneas de comisiones deben estar sin monto pagado')
            #comerciantes = list(set([int(x.comercial.id) for rec.line_ids]))
            comerciantes = list(set([x.comercial for x in rec.line_ids]))
            for c in comerciantes:
                total = sum(rec.line_ids.filtered(lambda x: x.comercial==c).mapped('amount_total'))
                if total == 0.0:
                    raise UserError('El monto a pagar no debe ser cero')
                vals = {
                'date': fields.Datetime.now(),
                'journal_id': rec.journal_id.id,
                'line_ids': False,
                'state': 'draft',
                'partner_id': c.id,
                'move_type':'in_invoice',
                'commission_id_full':rec.id,
                }
                move_apply_id = self.env['account.move'].sudo().create(vals)
                move_advance = {
                    'account_id': rec.product_id.categ_id.property_account_expense_categ_id.id,
                    'product_id': rec.product_id.id,
                    'company_id': rec.company_id.id,
                    'currency_id': False,
                    'date_maturity': False,
                    'date': fields.Datetime.now(),
                    'partner_id': c.id,
                    'move_id': move_apply_id.id,
                    'name': 'Pago de Comisiones' ,
                    'journal_id': rec.journal_id.id,
                    'debit': total,
                    'credit': 0.0,
                }
                asiento = move_advance
                move_line_obj = self.env['account.move.line']
                move_line_id1 = move_line_obj.with_context(check_move_validity=False).sudo().create(asiento)
                move_apply_id.with_context(check_move_validity=False)._onchange_partner_id()
                move_apply_id.with_context(check_move_validity=False).sudo().action_post()
            rec.state = 'done'
    #Chequea que no se añadan dos Líneas iguales
    @api.constrains('line_ids')
    def _check_exist_line_ids(self):
        for rec in self:
            existe_line_list = []
            for line in rec.line_ids:
                if line.commission_line_id.id in existe_line_list:
                    raise ValidationError(_("No se puede ingresar dos veces la misma línea - %s") % (line.commission_line_id.name)) 
                existe_line_list.append(line.commission_line_id.id)

    @api.depends('invoice_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.invoice_ids)

    def show_payments(self):
        self.ensure_one()
        res = self.env.ref('account.action_move_in_invoice_type')
        res = res.read()[0]
        res['context'] = {'create':False}
        res['domain'] = str([('commission_id_full', '=', self.id)])
        return res
    
    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('sale.commision.full.seq')
        vals.update({
            'name': name
            })
        res = super(SaleCommissionFullPayment, self).create(vals)
        return res   

class SaleCommissionFullPaymentLine(models.Model):
    _name = "sale.commission.full.line"
    _description = "Commission Payment Full Line"
    _inherit= ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Nombre",readonly=True,required=True,default='/')
    full_id = fields.Many2one('sale.commission.full',string="Pago en Lote Vinculado")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, related="full_id.company_id")
    commission_line_id = fields.Many2one('sale.commission.line',string="Línea de Comisión",domain="[('amount_paid','=',0)]",store=True,required=True)
    comercial = fields.Many2one("res.partner",string="Comisionista",readonly=True,required=True,related="commission_line_id.comercial",store=True)
    sale_id = fields.Many2one('sale.order',string="Venta Asociada",readonly=True,related="commission_line_id.sale_id",store=True)
    invoice_id = fields.Many2one('account.move',string="Factura Asociada",readonly=True,related="commission_line_id.invoice_id",store=True)
    partner_id = fields.Many2one('res.partner',string="Cliente",readonly=True,related="commission_line_id.partner_id",store=True)
    amount_total = fields.Float(string="Monto Total de Comisiones",readonly=True,defalt=0,required=True,related="commission_line_id.amount_total")

    @api.onchange('commission_line_id')
    def onchange_commission_line_id(self):
        for rec in self:
            rec.name = rec.commission_line_id.name or '/'