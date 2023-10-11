# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintellecs.com>).
#
##############################################################################
from datetime import datetime, timedelta
from odoo import api, models

class print_payment_report(models.AbstractModel):
    _name = 'report.dev_product_inventory_status.product_template_report'
        

    def all_product_data(self,data):
        product_id = []
        prod_data = []
        if data and self.env.company.product_inventory_status:
            product_ids = []
            domain = [('type','=','product')]
            company_id=  self.env.company
            if company_id.filter_by == 'category':
                domain.append(('categ_id','child_of',company_id.category_id.id))
            
            product_ids = self.env['product.product'].search(domain)
            if product_ids:
                for product in product_ids: 
                    prod_data.append({  'code':product.default_code or ' ',
                                        'product':product.display_name or ' ',
                                        'on_hand':product.qty_available or 0.00,
                                        'forecasted_qty':product.virtual_available or 0.00,
                                        'cost_price':product.standard_price or 0.00,
                                        'sale_price':product.list_price or 0.00,
                                            })
            
        if prod_data:
            if company_id.order_by == 'ascending':
                prod_data = sorted(prod_data, key = lambda i: i['on_hand'])
            else:
                prod_data = sorted(prod_data, key = lambda i: i['on_hand'], reverse=True)
        return prod_data
        
        
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.users'].browse(docids)
        
        return {
            'doc_ids': docs.ids,
            'doc_model': 'product.template',
            'docs': docs,
            'all_product_data': self.all_product_data(docs),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
