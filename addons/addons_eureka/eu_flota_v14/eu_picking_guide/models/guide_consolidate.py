# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError,ValidationError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

class GuideConsolidate(models.Model):
    _name = 'guide.consolidate'
    _description ="Picking Guide"
    _order = 'date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="New Guide Picking", readonly=True, default='New Guide Picking',track_visibility='always',) 
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,track_visibility='always',invisible=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'To Dispatch'),
        ('done', 'Confirmed'),
        ('cancel', 'Cancel'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='always', default='draft')

    # Fechas
    scheduled_date  = fields.Datetime(string="Scheduled Date",track_visibility='always',default=lambda self: fields.Date.to_string(datetime.now()))
    date            = fields.Date(string="Date",track_visibility='always',default=lambda self: fields.Date.to_string(date.today()),readonly=True)
    
    # Vehículo, Conductor y Placa
    vehicle_id      = fields.Many2one('fleet.vehicle', string="Vehicle", track_visibility='always')
    weight_capacity = fields.Float(related="vehicle_id.weight_capacity",string="Weight Capacity",tracking=True,store=True)
    volume_capacity = fields.Float(related="vehicle_id.volume_capacity",string="Volume Capacity",tracking=True,store=True)
    driver_id       = fields.Many2one('res.partner', related="vehicle_id.driver_id", string="Driver",store=True)
    license_plate   = fields.Char(string="Plate", related="vehicle_id.license_plate",store=True)

    # Firma
    signature       =  fields.Binary(string="Signature")

    # Líneas de la Guía
    guide_signature_line = fields.One2many(
        comodel_name='guide.consolidate.line',
        inverse_name='guide_consolidate_id_line',
        string='Picking Guide Line',
    )
    # Línea de Productos de las SU
    guide_signature_products = fields.One2many(
        comodel_name='guide.consolidate.product',
        inverse_name='guide_consolidate_id_product',
        string='Picking Guide Products',
    )

    #Zona de los pedidos
    zona = fields.Many2one(
        'partner.zone',
        string="Zone",
        readonly=True,
        store=True,
        required=True,
        tracking=True
    )

    # Total de Productos en las SU
    total = fields.Float(
        string="Total Qty",
        compute="_compute_total_qty",
        store=True,
    )
    # Total de Peso en las SU
    total_weight = fields.Float(
        string="Total Weight",
        compute="_compute_total_weight_volume",
    )
    # Total Volumen en las SU
    total_volume = fields.Float(
        string="Total Volume",
        compute="_compute_total_weight_volume",
    )
    # Restante de Peso 
    remaining_weight = fields.Float(
        string="Remaining Weight",
        compute="_compute_total_weight_volume",
    )
    # Restante Volumen
    remaining_volume = fields.Float(
        string="Remaining Volume",
        compute="_compute_total_weight_volume",
    )
    # Número de Precinto
    precint_number = fields.Char(string="Precint Number",tracking=True)
    # Total Monto de Facturas
    total_amount = fields.Float(
        string="Monto de las Facturas",
        compute="_compute_total_invoice"
    )
    # Total Monto de Facturas en REF
    total_amount_ref = fields.Float(
        string="Monto de las Facturas Ref",
        compute="_compute_total_invoice_ref"
    )
    cestas_qty = fields.Float(string="Cantidad de Cestas")
    cestas_peso = fields.Float(string="Peso de la Cesta (Unidad)")
    cestas_total = fields.Float(string="Total Peso Cestas",compute="_compute_cestas_total",store=True,readonly=True)

    # Traer SU por Zonas NO despachadas y VALIDADAS
    @api.onchange('zona')
    def onchange_zona(self):
        line_dict = {}
        for rec in self:
            if rec.zona:
                if rec.guide_signature_line:
                    for lines in rec.guide_signature_line:
                        values = [(5, 0, 0)]
                        rec.update({'guide_signature_line': values})
                if rec.guide_signature_products:
                    for lines in rec.guide_signature_products:
                        values = [(5, 0, 0)]
                        rec.update({'guide_signature_products': values})
                orders = [line for line in sorted(rec.env['stock.picking'].search([('partner_id.zone', '=', rec.zona.id),('state', '=', 'done'),('dispatch_status', '=', 'no_dispatch'),('picking_type_id.code', '=', 'outgoing')]),
                    key=lambda x: x.id)]
                for order in orders:
                    line_dict = {
                        'name':  str(order.name) + ' - ' + str(order.partner_id.name),
                        'picking_id':  order.id,
                        'partner_id':  order.partner_id.id,
                        'invoice_rel': self.env['account.move'].search([('name','=',order.invoice_rel)],limit=1).id,
                        'zona':        order.partner_id.zone.id,
                    }
                    lines = [(0,0,line_dict)]
                    rec.write({'guide_signature_line':lines})
                if not line_dict:
                    raise Warning(_("Nothing to Dispatch."))
    
    # Función Computada para obtener el Total Peso de Cestas
    @api.depends('cestas_peso','cestas_qty')
    def _compute_cestas_total(self):
        for rec in self:
            rec.cestas_total = rec.cestas_peso * rec.cestas_qty

    # Función Computada para obtener el Total
    @api.depends('guide_signature_line')
    def _compute_total_qty(self):
        for rec in self:
            rec.total = 0.0
            if rec.guide_signature_line:
                for lines in rec.guide_signature_line:
                    rec.total += lines.total_items
    
    # Función Computada para obtener el Total del Peso, el Total de Volumen, Peso y Volumen Restante
    @api.depends('guide_signature_products','cestas_total')
    def _compute_total_weight_volume(self):
        for rec in self:
            rec.total_weight = sum(rec.guide_signature_products.mapped(lambda x: x.quantity_done * x.product_id.weight)) + rec.cestas_total
            rec.total_volume = sum(rec.guide_signature_products.mapped(lambda x: x.quantity_done * x.product_id.volume)) + rec.cestas_total
            rec.remaining_weight = rec.total_weight - rec.weight_capacity
            rec.remaining_volume = rec.total_volume - rec.volume_capacity
    
    # Función Computada para obtener el Total de las facturas
    @api.depends('guide_signature_line')
    def _compute_total_invoice(self):
        for rec in self:
            rec.total_amount = 0.0
            if rec.guide_signature_line:
                for lines in rec.guide_signature_line.filtered(lambda x: x.invoice_rel):
                    rec.total_amount += lines.invoice_rel.amount_total if lines.invoice_rel.currency_id == lines.invoice_rel.company_id.currency_id else lines.invoice_rel.amount_ref
    
    # Función Computada para obtener el Total de las facturas REF
    @api.depends('guide_signature_line')
    def _compute_total_invoice_ref(self):
        for rec in self:
            rec.total_amount_ref = 0.0
            if rec.guide_signature_line:
                for lines in rec.guide_signature_line.filtered(lambda x: x.invoice_rel):
                    rec.total_amount_ref += lines.invoice_rel.amount_total if lines.invoice_rel.currency_id != lines.invoice_rel.company_id.currency_id else lines.invoice_rel.amount_ref
    # Evitar eliminación
    def unlink(self):
        for rec in self:
            if rec.name != 'New Guide Picking':
                raise UserError(_("You cannot delete a Picking Guide that is already waiting."))
            for picking in rec.guide_signature_line.picking_id:
                picking.dispatch_status = 'no_dispatch'
        return super(GuideConsolidate, self).unlink()
    
    # Pasar a Borrador
    def reset_draft(self):
        for rec in self:
            for picking in rec.guide_signature_line.picking_id:
                picking.dispatch_status = 'no_dispatch'
            rec.state = 'draft'
    
    # Pasar en Espera por despacho
    def button_waiting(self):
        for rec in self:
            if not rec.guide_signature_line:
                raise Warning(_('Please, add a line in Picking Guide Line.'))
            for picking in rec.guide_signature_line.picking_id:
                if picking.dispatch_status != 'no_dispatch':
                    raise Warning(_('Some pickings is already added in other Picking Guide. - %s') % (picking.name))
                picking.dispatch_status = 'to_dispatch'
            rec.products_obtain()
            rec.state = 'waiting'
    
    # Botón para Cambiar Número de Precinto
    def button_reprecint(self):
        return self.env['guide.consolidate.reprecint']\
            .with_context(active_ids=self.ids, active_model='guide.consolidate', active_id=self.id)\
            .action_reprecint()

    # Botón Confirmar Guía de Despacho y se le asigna su sequence
    def button_confirm(self):
        for rec in self:
            if self.name == 'New Guide Picking':
                self.name = self.env['ir.sequence'].next_by_code('guide.consolidate.seq')
            if not rec.signature:
                raise Warning(_('Please, add a signature.'))
            self.products_obtain()
            if not rec.vehicle_id:
                raise Warning(_('Please, choose a Vehicle.'))
            for picking in rec.guide_signature_line.picking_id:
                if picking.dispatch_status != 'to_dispatch':
                    raise Warning(_('Some pickings is already added in other Picking Guide. - %s') % (picking.name))
                picking.dispatch_status = 'dispatched'
                picking.fleet = rec.vehicle_id.id
            rec.state = 'done'
    
    # Botón para Cancelar
    def button_cancel(self):
        for rec in self:
            for picking in rec.guide_signature_line.picking_id:
                picking.dispatch_status = 'no_dispatch'
            if rec.guide_signature_line:
                for lines in rec.guide_signature_line:
                    values = [(5, 0, 0)]
                    rec.update({'guide_signature_line': values})
            if rec.guide_signature_products:
                for lines in rec.guide_signature_products:
                    values = [(5, 0, 0)]
                    rec.update({'guide_signature_products': values})
            rec.state = 'cancel'
    
    # Botón para actualizar facturas
    def button_actualizar_facturas(self):
        for rec in self:
            if rec.guide_signature_line:
                for lines in rec.guide_signature_line:
                    lines.invoice_rel = self.env['account.move'].search([('name','=',lines.picking_id.invoice_rel)],limit=1).id,
                    
    # Botón para traer los productos
    def products_obtain(self):
        order = []
        lines = []
        product_ids = []
        for rec in self:
            if rec.guide_signature_products:
                for products in rec.guide_signature_products:
                    products.unlink()
            if rec.guide_signature_line:
                orders = [line for line in sorted(rec.guide_signature_line.picking_id.move_ids_without_package, key=lambda x: x.product_id.id)]
                for order in orders:
                    if order.product_id.id not in product_ids:
                        product_ids.append(order.product_id.id)

                for id in product_ids:
                    product_id      = ''
                    product_name      = ''
                    quantity_done   = 0.0
                    for order in orders:
                        if id==order.product_id.id:
                            quantity_done += order.quantity_done
                            product_id = order.product_id.id
                            product_name = order.product_id.name
                            weight = order.product_id.weight
                            volume = order.product_id.volume
                    lines.append((0,0,{
                            'name':  str(product_name),
                            'product_id':       product_id,
                            'quantity_done':    quantity_done,
                            'weight':           quantity_done*weight,
                            'volume':           quantity_done*volume,
                            }))
                rec.write({'guide_signature_products':lines})
            else:
                raise UserError(_("Please, add a Picking to obtain some products."))
    
    #Chequea que no se añadan dos SU iguales
    @api.constrains('guide_signature_line')
    def _check_exist_product_in_line(self):
        for rec in self:
            exist_picking_list = []
            for line in rec.guide_signature_line:
                if line.picking_id.id in exist_picking_list:
                    raise ValidationError(_("You can't repeat a Picking - %s") % (line.picking_id.name)) 
                exist_picking_list.append(line.picking_id.id)