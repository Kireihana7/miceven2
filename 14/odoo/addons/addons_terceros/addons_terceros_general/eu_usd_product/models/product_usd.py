# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    currency_id_dif = fields.Many2one("res.currency", 
    string="Divisa Dolar",invisible=True,
    default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)

    currency_id_ves = fields.Many2one("res.currency", 
    string="Divisa Bolivar",invisible=True,
    default=lambda self: self.env['res.currency'].search(['|',('name', '=', 'VES'),('name', '=', 'VEF')], limit=1),)

    currency_id = fields.Many2one(
    default=lambda self: self.env.company.currency_id)

   
    @api.depends('currency_id_dif','currency_id','list_price')
    def _amount_all_usd_sale(self):

        for record in self:
            record.amount_total_usd_sale = 0
            if record.standard_price != 0:  
                record.amount_total_usd_sale   = record.env.company.currency_id._convert(record['list_price'], record.currency_id_dif, record.company_id or record.env.company, fields.date.today())
    
    @api.depends('standard_price','currency_id_dif','currency_id')
    def _amount_all_usd(self):
        for record in self:
            record.amount_total_usd    = 0
            record.tax_today           = record.currency_id_dif._convert(1, record.currency_id_ves, record.company_id or record.env.company, fields.date.today())
            if record.standard_price != 0:  
                record.amount_total_usd        = record.env.company.currency_id._convert(record['standard_price'], record.currency_id_dif, record.company_id or record.env.company, fields.date.today())


    tax_today= fields.Float(store=True,readonly=True, compute="_amount_all_usd", default=0,string="Tasa") 
    amount_total_usd = fields.Float(string='Costo $', store=True, readonly=True, compute='_amount_all_usd', tracking=4, default=0)
    amount_total_usd_sale = fields.Float(string='Precio de Venta $', store=True, readonly=True, compute='_amount_all_usd_sale', tracking=4, default=0)
    
    total=fields.Float(string='Costo Total Bs', compute='_totalizar')
    total_sale=fields.Float(string='Precio de Venta Total Bs', compute='_totalizar')
    totalusd=fields.Float(string='Coste Total $', compute='_totalizar')
    totalusd_sale=fields.Float(string='Precio de Venta Total $', compute='_totalizar')

    @api.depends('qty_available','standard_price')
    def _totalizar(self):
        for record in self:
            record[("total")]           = (record.env.company.currency_id._convert(record['standard_price'], record.currency_id_ves, record.company_id or record.env.company, fields.date.today())) *record.qty_available
            record[("total_sale")]      = (record.env.company.currency_id._convert(record['list_price'],     record.currency_id_ves, record.company_id or record.env.company, fields.date.today())) *record.qty_available
            record[("totalusd")]        = (record.env.company.currency_id._convert(record['standard_price'], record.currency_id_dif, record.company_id or record.env.company, fields.date.today())) *record.qty_available
            record[("totalusd_sale")]   = (record.env.company.currency_id._convert(record['list_price'],     record.currency_id_dif, record.company_id or record.env.company, fields.date.today())) *record.qty_available
