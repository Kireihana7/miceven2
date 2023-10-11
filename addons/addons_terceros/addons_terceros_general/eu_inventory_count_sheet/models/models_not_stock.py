# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError

class ParticularReportA(models.AbstractModel):
    _name = 'report.eu_inventory_count_sheet.eu_inv_count_n_stock'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        
        # return a custom rendering context
        return {
            'doc_ids':docids,
            'doc_model': 'stock.count.sheet.notstock',
            'docs':docids,
            'datas':data

        }

class StockSheetCountNotStock(models.TransientModel):
    _name = 'stock.count.sheet.notstock'
    _description = "Stock sheet count Report not stock"

    location_id = fields.Many2many('stock.location', string='Ubicación',required=True,domain=[('usage', '=', 'internal')])
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )

    @api.onchange('wherehouse_id')
    def _onchage_location_id(self):
        if self.location_id:
            self.location_id = False

    def print_report(self):
        domain = []
        datas = []
        ids_l = []
        ids_name = []

        #for rec in self.location_id:
        #    ids_l.append({
        #        'location_id': rec.id,
        #        'complete_name': rec.complete_name,
        #        })
        
        stocks = self.env["stock.quant"].sudo().search(
        [
        ('location_id', 'in', self.location_id.ids), 
        ('company_id', '=', self.company_id.id),
        ],order='product_id asc'
        )
        if not stocks:
            raise UserError('No se encontraron registros.')
        for stock in stocks:
            for rec in self.location_id:
                if rec.id == stock.location_id.id:
                    if stock.location_id.id not in ids_l:
                        ids_l.append(stock.location_id.id)
                        ids_name.append(stock.location_id.complete_name)

            secondary_uom_onhand = 0
            if stock.product_id.product_tmpl_id.secondary_uom:
                    secondary_uom_onhand = stock.product_id.product_tmpl_id.uom_id._compute_quantity(stock.quantity, stock.product_id.product_tmpl_id.secondary_uom)

            datas.append({
                'name':         stock.location_id.complete_name,
                'id_location':  stock.location_id.id,
                'default_code': stock.product_id.product_tmpl_id.default_code,
                'product':      stock.product_id.name,
                'qty':          stock.quantity,
                'uom':          stock.product_id.product_tmpl_id.uom_id.name,
                'secondary_uom':stock.product_id.product_tmpl_id.secondary_uom.name if stock.product_id.product_tmpl_id.secondary_uom.name else 'N/A',
                'qty_usec'    : secondary_uom_onhand if secondary_uom_onhand else 'N/A' ,
                })
        data = {
            'company_name':     self.company_id.name,
            'company_vat':      self.company_id.vat,
            #'name':             self.location_id.complete_name,
            'today':            fields.Datetime.today(),
            'realizado':        self.env.user.name,
            'arreglo':          datas,
            'ids_l':            ids_l,
            'ids_name':         ids_name,
        }
        return self.env.ref('eu_inventory_count_sheet.eu_inv_count_n_stock').report_action(self,data=data)