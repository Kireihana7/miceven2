# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import  UserError

class ChargueMultiWeight(models.Model):
    _name = 'chargue.multi.weight'
    _description ="Tabla para Multi Pesado"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    chargue_consolidate = fields.Many2one('chargue.consolidate',string="Orden Romana")
    #state = fields.Selection(related="chargue_consolidate.state", string='Estatus')
    #with_trailer    = fields.Boolean(related="chargue_consolidate.with_trailer",string="¿Tiene Remolque?")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    # Pesos Romana (Bruto, Tara, Neto)
    
    product_id = fields.Many2one('product.template',string="Producto")
    warehouses_id = fields.Many2one('stock.warehouse',string="Almacén")
    sale_ids = fields.Many2one('sale.order',string="Orden de Venta")
    purchase_id = fields.Many2one('purchase.order',string="Orden de Compra")
    picking_ids = fields.Many2many(
        "stock.picking",
        "chargue_multi_weight_picking_rel",
        "multi_weight_id",
        "picking_id",
        string="SU",
    )
    peso_su = fields.Float('Peso del Pedido',compute="_compute_peso_su")

    @api.onchange('sale_ids')
    def onchange_sale_ids(self):
        for rec in self:
            rec.warehouses_id = rec.sale_ids.warehouse_id.id
            rec.picking_ids = rec.sale_ids.picking_ids.ids

    @api.depends('picking_ids')
    def _compute_peso_su(self):
        for rec in self:
            peso_su = rec.peso_su = 0.0

            if rec.picking_ids:
                for lines in rec.picking_ids.move_ids_without_package:
                    peso_su = lines.quantity_done * lines.product_id.weight
                    rec.peso_su += peso_su

    peso_bruto = fields.Float(
        string="Peso Bruto",
        store=True,
        tracking=True,
        readonly=True,
    )
    peso_tara = fields.Float(
        string="Peso Tara",
        store=True,
        tracking=True,
        readonly=True,
    )
    peso_bruto_trailer = fields.Float(
        string="Peso Bruto Trailer",
        store=True,
        tracking=True,
        readonly=True,
    )
    peso_tara_trailer = fields.Float(
        string="Peso Tara Trailer",
        store=True,
        tracking=True,
        readonly=True,
    )
    peso_neto = fields.Float(
        string="Peso Neto",
        store=False,
        compute="compute_peso_neto",
        tracking=True
    )
    peso_neto_trailer = fields.Float(
        string="Peso Neto Trailer",
        store=False,
        compute="compute_peso_neto_trailer",
        tracking=True
    )
    date_first_weight   = fields.Datetime(string="Primera Pesada",tracking=True,readonly=True)
    date_second_weight  = fields.Datetime(string="Segunda Pesada",tracking=True,readonly=True)
    date_first_weight_t = fields.Datetime(string="Primera Pesada Trailer",tracking=True,readonly=True)
    date_second_weight_t= fields.Datetime(string="Segunda Pesada Trailer",tracking=True,readonly=True)

    # Calculo de Peso Neto
    @api.depends('peso_bruto','peso_tara')        
    def compute_peso_neto(self):
        for rec in self:
            rec.peso_neto = rec.peso_bruto - rec.peso_tara

    # Calculo de Peso Neto Trailer
    @api.depends('peso_bruto_trailer','peso_tara_trailer')
    def compute_peso_neto_trailer(self):
        for rec in self:
            rec.peso_neto_trailer = rec.peso_bruto_trailer - rec.peso_tara_trailer

    def action_peso_manual(self):
        return self.env['chargue.manual']\
            .with_context(active_ids=self.ids, active_model='chargue.multi.weight', active_id=self.id, chargue_consolidate=self.chargue_consolidate.id)\
            .action_register_manual()
        # Botón Obtener Peso Bruto
    def obtener_peso_bruto(self):
         for rec in self:
            if not rec.chargue_consolidate.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')

            balanza = rec.chargue_consolidate.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_bruto": balanza,
                    "date_first_weight": fields.Datetime.now()
                })
            
    # Botón Obtener Peso Bruto
    def obtener_peso_tara(self):
         for rec in self:
            if not rec.chargue_consolidate.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')

            balanza = rec.chargue_consolidate.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_tara": balanza,
                    "date_second_weight": fields.Datetime.now()
                })
            
    # Botón Obtener Peso Bruto
    def obtener_peso_bruto_trailer(self):
         for rec in self:
            if not rec.chargue_consolidate.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')

            balanza = rec.chargue_consolidate.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_bruto_trailer": balanza,
                    "date_first_weight_t": fields.Datetime.now()
                })
            
    # Botón Obtener Peso Bruto
    def obtener_peso_tara_trailer(self):
        for rec in self:
            if not rec.chargue_consolidate.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')

            balanza = rec.chargue_consolidate.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_tara_trailer": balanza,
                    "date_second_weight_t": fields.Datetime.now()
                })
            
