# -*- coding: utf-8 -*-

import string
import time, datetime
from odoo import models, fields,api

class ResTraceability(models.Model):
    _name ='res.traceability'
    _description = 'Trazabilidad de visitas'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Sale Order
    sale_order = fields.Many2one('sale.order', string="SO")
    create_date_so = fields.Datetime(string="Fecha de SO")
    branch_id = fields.Many2one(related='sale_order.branch_id', string="Rama SO", store=True)
    
    #Visitas
    sale_visii = fields.Many2one('res.visit', string="Visita") 
    fecha_visita = fields.Datetime("Fecha de Visita")
   
    #stock picking
    stock_picking= fields.Many2one('stock.picking' )
    date_done_stock=fields.Datetime(string="Fecha Salida de Inventario")
    
    # Facturacion
    account_move=fields.Many2one('account.move')
    invoice_date=fields.Datetime(string="fecha de Confirmacion de Factura")
    #Fecha tiempo total
    duracion_fecha= fields.Char(string="Relacion de Fecha")








        
    # #calculos
    # fecha_visita_a_so=fields.Datetime()
    # fecha_so_stock =fields.Datetime()
    # fecha_stock_invoice=fields.Datetime()




            #     rec.fecha_visita_a_so= rec.fecha_visita - rec.create_date_so
            
            # if rec.fecha_visita_a_so and rec.date_done_stock:
                
            #     rec.fecha_so_stock= rec.fecha_visita_a_so - rec.date_done_stock

            # if rec.fecha_so_stock and rec.invoice_date:

            #     rec.fecha_stock_invoice= rec.fecha_so_stock - rec.invoice_date


