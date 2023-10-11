# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import pytz
import datetime


class AccountDotmatrixReceipt(models.TransientModel):
    _name = 'account.dotmatrix.receipt'

    name = fields.Char("Test")


class AccountMove(models.Model):
    _inherit = "account.move"
 
    def print_new_receipt(self):
        templ = self.env.ref("invoice_dotmatrix_printer.template_dotmatrix_ai")
        if templ:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'account.move', [self.id])
            view_id = self.env.ref('invoice_dotmatrix_printer.account_dotmatrix_receipt_form').id
            res = {
            	"name":data[self.id],
            }
            wizard_id = self.env['account.dotmatrix.receipt'].create(res)
            context = self._context.copy()
            return {
                'name':'Print Receipt',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(view_id,'form')],
                'res_model':'account.dotmatrix.receipt',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'res_id':wizard_id.id,
                'target':'new',
                'context':context,

            }

class Picking(models.Model):
    _inherit = "stock.picking"

    def print_new_receipt_picking(self):
        templ = self.env.ref("invoice_dotmatrix_printer.template_dotmatrix_ai_picking")#el id del mail.template
        if templ :
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'stock.picking', [self.id])
            view_id = self.env.ref('invoice_dotmatrix_printer.dotmatrix_receipt_form_picking').id #el id del la ventana modal (record)
            res = {
                "name":data[self.id],
            }
            wizard_id  = self.env['account.dotmatrix.receipt'].create(res)
            context = self._context.copy()
            return {

                'name':'Imprimir Nota de Entrega',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(view_id,'form')],
                'res_model':'account.dotmatrix.receipt',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'res_id':wizard_id.id,
                'target':'new',
                'context':context,

            }

    total_qty = fields.Float(string="Total QTY", compute="_totales")
    total_uom = fields.Float(string="Total Uom", compute="_totales")
    @api.depends('move_ids_without_package')
    def _totales(self):
        for picking in self:
            picking.total_qty = 0
            picking.total_uom = 0
            for line in picking.move_ids_without_package.filtered(lambda line: line.state =='done'):
                picking.total_qty += line.product_uom_qty
                picking.total_uom += line.weight_line


class StockMove(models.Model):
    _inherit = "stock.move"
    weight_line = fields.Float(string="Peso", compute="_compute_peso")

    @api.depends('product_uom_qty','product_id.weight')
    def _compute_peso(self):
        for picking in self:
            picking.weight_line = False
            if picking.product_id.weight <= 0:
                picking.weight_line = round(picking.product_uom_qty)
            if picking.product_id.weight > 0:
                picking.weight_line = round((picking.product_uom_qty * picking.product_id.weight))

class ChargueConsolidate(models.Model):
    _inherit = 'chargue.consolidate'
    _description = 'Gestion de Romana'

    is_print_1 = fields.Boolean(string="¿Ha Impreso Ticket Peso Tara?") #primera pesada en venta segunda en compra
    is_print_2 = fields.Boolean(string="¿Ha Impreso Ticket Peso Bruto?")#segunda pesada venta primera en compra


    def print_new_receipt_romana(self):
        templ = self.env.ref("invoice_dotmatrix_printer.template_dotmatrix_romana") # id del mail.template 
        if templ:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'chargue.consolidate', [self.id])
            view_id = self.env.ref('invoice_dotmatrix_printer.dotmatrix_receipt_form_romana').id # id del record (vista modal )
            res = {
                "name":data[self.id],
            }
            wizard_id = self.env['account.dotmatrix.receipt'].create(res)
            context = self._context.copy()
            
            if self.operation_type == 'venta' and self.state == 'cargando':
                self.is_print_1 = True
            if self.operation_type == 'venta' and self.state == 'descargando':
                self.is_print_2 = True
            if self.operation_type == 'compra' and self.state == 'descargando':
                self.is_print_2 = True
            if self.operation_type == 'compra' and self.state == 'cargando':
                self.is_print_1 = True            
            
            return {
                'name':'Print Receipt',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(view_id,'form')],
                'res_model':'account.dotmatrix.receipt',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'res_id':wizard_id.id,
                'target':'new',
                'context':context,
            }
    h_actual_b_pesaje = fields.Char(string="Hora actual de Pesaje",compute="_hora_pesaje")
    date_first_weight_report = fields.Char(string="Hora actual de Pesaje",compute="_hora_pesaje")
    date_second_weight_report = fields.Char(string="Hora actual de Pesaje",compute="_hora_pesaje")
   
    
    @api.depends('date_first_weight','date_second_weight')
    def _hora_pesaje(self):
        self.h_actual_b_pesaje = (datetime.datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M %p')
        self.date_first_weight_report =  self.date_first_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if self.date_first_weight else False
        self.date_second_weight_report =  self.date_second_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if self.date_second_weight else False

    # date_first_weight_mp = fields.Char(string="Hora actual de Pesaje",compute="_fecha_format")
    # date_second_weight_mp = fields.Char(string="Hora actual de Pesaje",compute="_fecha_format")


    
    # @api.depends('multi_weight')
    # def _fecha_format(self):
    #     for x in self.multi_weight:
    #         self.date_first_weight_mp =  x.date_first_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if x.date_first_weight else False
    #         self.date_second_weight_mp = x.date_second_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if x.date_second_weight else False

    def print_orden_carga_romana(self):
        templ = self.env.ref("invoice_dotmatrix_printer.template_dotmatrix_romana_orden_carga") # id del mail.template 
        if templ:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'chargue.consolidate', [self.id])
            view_id = self.env.ref('invoice_dotmatrix_printer.dotmatrix_orden_carga_romana').id # id del record (vista modal )
            res = {
                "name":data[self.id],
            }
            wizard_id = self.env['account.dotmatrix.receipt'].create(res)
            context = self._context.copy()
 
            return {
                'name':'Print Receipt',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(view_id,'form')],
                'res_model':'account.dotmatrix.receipt',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'res_id':wizard_id.id,
                'target':'new',
                'context':context,
            }

class ChargueConsolidateMultiPeso(models.Model):
    _inherit = 'chargue.multi.weight'

    date_first_weight_1    = fields.Char(string="Primera Pesada",compute='_fecha_format')
    date_second_weight_2   = fields.Char(string="Segunda Pesada",compute='_fecha_format')
    #date_first_weight_t_1  = fields.Char(string="Primera Pesada Trailer",)
    #date_second_weight_t_2 = fields.Char(string="Segunda Pesada Trailer",)

    @api.depends('date_first_weight', 'date_second_weight')
    def _fecha_format(self):
        for rec in self:
            rec.date_first_weight_1 =  rec.date_first_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if rec.date_first_weight else False
            rec.date_second_weight_2 = rec.date_second_weight.astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d %I:%M:%S') if rec.date_second_weight else False




             
                    






