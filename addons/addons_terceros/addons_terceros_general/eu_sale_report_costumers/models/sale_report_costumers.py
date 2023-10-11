# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleReportCostumers(models.TransientModel):
    _name = 'sale.report.costumers.wizard'
    _description = 'Report sale for costumers'

    desde = fields.Date('Desde', required=True)
    hasta = fields.Date('Hasta', required=True)
    partner_id = fields.Many2many('res.partner', String="Cliente")

    def print_report(self):
        data = []

        domain = [
            ('state','=','sale'),
            ('date_order','>=',self.desde),
            ('date_order','<=',self.hasta),
        ]

        if self.partner_id:
            domain.append(('partner_id','in', self.partner_id.ids))

        sales_order = self.env['sale.order'].search(domain)

        if len(sales_order) == 0:
            raise UserError("NO hay registros entre estas fechas...!")

        sum_total_fardos = sum(sales_order.mapped('order_line').mapped('product_uom_qty'))
        sum_fardos_despachados = sum(sales_order.mapped('order_line').mapped('qty_delivered'))
        sum_por_despachar = sum(sales_order.mapped('order_line').mapped(lambda x: x.product_uom_qty - x.qty_delivered))
        sum_total_kg = sum(sales_order.mapped('order_line').mapped(lambda x: x.product_uom_qty * 20))

        for sale in sales_order:
            for order in sale.order_line:
                data.append({
                    'partner': sale.partner_id.name,
                    'rif': sale.partner_id.vat,
                    'date_order': sale.date_order.strftime('%d/%m/%Y'),
                    'ciudad': sale.partner_id.city_id.name,
                    'vendedor': sale.user_id.name,
                    'producto': order.product_template_id.name,
                    'total_kg': "{0:.2f}".format((order.product_uom_qty) * 20),
                    'total_fardos': "{0:.2f}".format(order.product_uom_qty),
                    'fardos_despachados': "{0:.2f}".format(order.qty_delivered), 
                    'por_despachar': "{0:.2f}".format((order.product_uom_qty) - (order.qty_delivered)),
                })
       
        
        res={
            'desde': self.desde.strftime('%d/%m/%Y'),
            'hasta':self.hasta.strftime('%d/%m/%Y'),
            'docs': data,
            'sum_total_fardos': "{0:.2f}".format(sum_total_fardos),
            'sum_fardos_despachados': "{0:.2f}".format(sum_fardos_despachados),
            'sum_por_despachar': "{0:.2f}".format(sum_por_despachar),
            'sum_total_kg': "{0:.2f}".format(sum_total_kg),
        }

        data = {
            'form': res
        }

        return self.env.ref('eu_sale_report_costumers.custom_action_sale_report_costumers_wizard').report_action(self,data=data)
  




    
