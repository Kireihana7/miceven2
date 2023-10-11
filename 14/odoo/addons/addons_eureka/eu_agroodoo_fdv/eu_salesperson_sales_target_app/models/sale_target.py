# -*- coding: utf-8 -*-
from __future__ import division
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
import calendar

class SaleTarget(models.Model):
    _name="saletarget.saletarget"
    _description= "Sales Target"

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    sales_person_id = fields.Many2one('res.users',string="Salesperson")
#    sales_person_zone = fields.Many2one(related='sales_person_id.zone',string="Zona")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    date_today = fields.Date('Hoy', default=fields.Date.context_today, store=False,)
    target_achieve = fields.Selection([('Sale Order Confirm','Sale Order Confirm'),
                                ('Delivery Order Done','Delivery Order Done'),
                                ('Invoice Created','Invoice Created'),
                                ('Invoice Confirm','Invoice Confirm'),
                                ('Invoice Paid','Invoice Paid')],string="Objetivo a lograr por")
    target = fields.Integer(string="Target", compute="_compute_target", store=True, readonly=True)
    difference = fields.Integer(string="Difference",compute="_get_difference",store=True, readonly=True)
    achieve = fields.Integer(string="Achieve", compute="_compute_sales_target", store=True, readonly=True)
    cotizado = fields.Integer(string="Cotizado", compute="_compute_cotizado", store=True, readonly=True)
    achieve_percentage = fields.Integer(string="Achieve Percentage",compute="_get_achieve_percentage", readonly=True)
    progreso_porcentaje = fields.Integer(string="Progreso porc.",compute="_progreso_porcentaje", readonly=True)
    responsible_salesperson_id = fields.Many2one('res.users',string="Responsible Salesperson")
    target_line_ids = fields.One2many('targetline.targetline','reverse_id')
    sale_ids = fields.One2many('sale.order','saletarget_id')
    invoice_ids = fields.One2many('account.move','saletarget_id')
    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('cancelled', 'Cancelled'),
        ], string='Status', readonly=True, default='draft')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    dias_habiles = fields.Integer(
        string='Días Habiles',
        compute = '_compute_dias_habiles',
        store= True,
    )

    dias_transcurridos = fields.Integer(
        string='Días Transcurridos',
        compute = '_compute_dias_transcurridos',
    )  

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )

    @api.depends('sale_ids')
    def _compute_count_sales(self):
        for rec in self:
            rec.count_sales = len(rec.sale_ids)
            rec.count_invoices = len(rec.invoice_ids)

    count_sales = fields.Integer(string="Ventas Vinculadas",compute="_compute_count_sales")
    count_invoices = fields.Integer(string="Facturas Vinculadas",compute="_compute_count_sales")

    def show_sales(self):
        self.ensure_one()
        res = self.env.ref('sale.action_quotations_with_onboarding')
        res = res.read()[0]
        res['domain'] = str([('saletarget_id', '=', self.id)])
        return res

    def show_invoices(self):
        self.ensure_one()
        res = self.env.ref('account.action_move_out_invoice_type')
        res = res.read()[0]
        res['domain'] = str([('saletarget_id', '=', self.id)])
        return res

    @api.depends('start_date','end_date')
    def _compute_dias_habiles(self):
        
        for rec in self:
            contador=0
            contadort=0
            rec.dias_habiles = False
            formato = "%d/%m/%Y"
            if rec.start_date and rec.end_date:
                adesde=rec.start_date.year
                mdesde=rec.start_date.month
                ddesde= rec.start_date.day
                fechadesde = str(ddesde)+'/'+str(mdesde)+'/'+str(adesde)

                ahasta=rec.end_date.year
                mhasta=rec.end_date.month
                dhasta=rec.end_date.day
                monthRange = calendar.monthrange(ahasta, mhasta)
                #dhasta = monthRange[1]

                fechahasta = str(dhasta)+'/'+str(mhasta)+'/'+str(ahasta)
                fechadesded = datetime.strptime(fechadesde, formato)
                fechahastad = datetime.strptime(fechahasta, formato)
                while fechadesded <= fechahastad:
                    contadort +=1
                    if datetime.weekday(fechadesded) in (0,1,2,3,4):
                        contador +=1
                    fechadesded = fechadesded + timedelta(days=1)
                rec.dias_habiles=contador

    @api.depends('start_date','end_date')
    def _compute_dias_transcurridos(self):
        for rec in self:
            contador=0
            contadort=0
            formato = "%d/%m/%Y"
            rec.dias_transcurridos= False
            if rec.start_date or rec.end_date:
                adesde=rec.start_date.year
                mdesde=rec.start_date.month
                ddesde=rec.start_date.day
                fechadesde = str(ddesde)+'/'+str(mdesde)+'/'+str(adesde)

                ahasta=datetime.now().year
                mhasta=datetime.now().month
                dhasta=datetime.now().day
                monthRange = calendar.monthrange(ahasta, mhasta)
                #dhasta = monthRange[1]

                fechahasta = str(dhasta)+'/'+str(mhasta)+'/'+str(ahasta)
                fechadesded = datetime.strptime(fechadesde, formato)
                fechahastad = datetime.strptime(fechahasta, formato)
                while fechadesded <= fechahastad:
                    contadort +=1
                    if datetime.weekday(fechadesded) in (0,1,2,3,4):
                        if contador < rec.dias_habiles and rec.state != 'cancelled':
                            contador +=1
                    fechadesded = fechadesded + timedelta(days=1)
                rec.dias_transcurridos=contador
            
            

    def _progreso_porcentaje(self):
        for rec in self:
            if rec.dias_habiles > 0 and rec.state != 'cancelled':
                rec.progreso_porcentaje = (rec.dias_transcurridos / rec.dias_habiles) * 100
                if rec.dias_transcurridos >= rec.dias_habiles:
                    rec.progreso_porcentaje = 100    
            else:
                rec.progreso_porcentaje = 0

    @api.depends('target_line_ids','target_line_ids.target_quantity')
    def _compute_target(self):
        for record in self:
            record.target = sum([line.target_quantity for line in record.target_line_ids])

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('saletarget.sequence') or _('New')
        result = super(SaleTarget, self).create(vals)
        return result

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('You can only delete an sales target in draft state.'))
        return super(SaleTarget, self).unlink()

    def confirm(self):
        count=0
        for i in self:
            if i.target <= 0:
                raise UserError("Target Must be Grater then 0.")
        for j in self.target_line_ids:
            count+=j.target_quantity
            if count > i.target:
                raise UserError("Target Quantity Must be same as Target or Less.")
        return self.write({'state':'open'})

    def close(self):
        return self.write({'state':'closed'})

    def cancel(self):
        return self.write({'state':'cancelled'})


    @api.depends('target_line_ids','target_line_ids.achieve_quantity')
    def _compute_sales_target(self):
        for record in self:
            record.achieve = sum([line.achieve_quantity for line in record.target_line_ids])

    @api.depends('target_line_ids','target_line_ids.cotizado')
    def _compute_cotizado(self):
        for record in self:
            record.cotizado = sum([line.cotizado for line in record.target_line_ids])

    @api.depends('achieve','target')
    def _get_achieve_percentage(self):
        for record in self:
            try:
                record.achieve_percentage=record.achieve * 100/record.target
            except ZeroDivisionError:
                return record.achieve_percentage

    @api.depends('achieve','target')                   
    def _get_difference(self):
        self.difference=self.target - self.achieve

    def send_mail(self):
        template_id = self.env['ir.model.data'].get_object_reference('eu_salesperson_sales_target_app','sales_person_send_mail')[1]
        email_template_obj = self.env['mail.template'].browse(template_id)
        if template_id:
            values = email_template_obj.generate_email(self.id, fields=None)
            values['email_from'] = self.env.user.email
            values['email_to'] = self.sales_person_id.partner_id.email
            values['author_id'] = self.env.user.partner_id.id
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.sudo().create(values)
            if msg_id:
                msg_id.sudo().send()

    def recompute_data(self):
        for lines in self.target_line_ids:
            lines.write({'achieve_quantity': 0,'cotizado':0})
        for rec in self:
            account_move = self.env['account.move'].search([
                        ('invoice_user_id','=', rec.sales_person_id.id),
                        ('state','=', 'posted'),
                        ('date','>=', rec.start_date),
                        ('date','<=', rec.end_date),
                        ('move_type','in',('out_refund','out_invoice')),
                        ])
            for account in account_move:
                for invoice_line in account.invoice_line_ids:
                    for target_line in rec.target_line_ids:
                        if invoice_line.product_id == target_line.product_id:
                            if account.move_type == 'out_invoice':
                                achieve_quantity = target_line.achieve_quantity + invoice_line.quantity
                            if account.move_type == 'out_refund':
                                achieve_quantity = target_line.achieve_quantity - invoice_line.quantity
                            target_line.write({'achieve_quantity': achieve_quantity})

            sale_order = self.env['sale.order'].search([
                        ('user_id','=', rec.sales_person_id.id),
                        ('state','in', ('sale','done')),
                        ('date_order','>=', rec.start_date),
                        ('date_order','<=', rec.end_date),
                        ])
            for sale in sale_order:
                for sale_line in sale.order_line:
                    for target_line in rec.target_line_ids:
                        if sale_line.product_id == target_line.product_id:
                            cotizado = target_line.cotizado + sale_line.product_uom_qty
                            target_line.write({'cotizado': cotizado})

class TargetLine(models.Model):
    _name="targetline.targetline"
    _description= "Sales Target Line"

    name = fields.Char(related="product_id.product_tmpl_id.name",string="Name",store=True)
    reverse_id = fields.Many2one('saletarget.saletarget')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    target_quantity = fields.Integer(string="Target Quantity", required=True)
    achieve_quantity = fields.Integer(string="Achieve Quantity", readonly=True)
    cotizado = fields.Integer(string="Cantidad Cotizada", readonly=True)
    achieve_perc = fields.Integer(string="Achieve Percentage",compute="_get_percentage",store=True)

    sales_person_id = fields.Many2one(related='reverse_id.sales_person_id', string="Vendedor")
#    sales_person_zone = fields.Many2one(related='reverse_id.sales_person_id.zone',string="Zona")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        copy=False,
        readonly=1,
        related="reverse_id.company_id"
    )
       
    @api.depends('target_quantity','achieve_quantity')                   
    def _get_percentage(self):
        for temp in self:
            try:
                temp.achieve_perc=temp.achieve_quantity * 100/temp.target_quantity
            except ZeroDivisionError:
                return temp.achieve_perc

