from odoo import http
from odoo.http import request
import time
import datetime
import json
from odoo import api
from odoo.tools import misc

from odoo import api, fields, models
from odoo.exceptions import UserError


from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import calendar

import logging
_logger = logging.getLogger(__name__)


class Academy(http.Controller):

    def _get_url(self, location=False):
        location = location.split('cids')
        location2 = location[1].split('&')
        location3 = location2[0].split('=')
        location4 = location3[1].split(',')
        company_ids = []
        for x in location4:
            company_ids.append(int(x))
        #raise UserError(company_ids)
        return company_ids

    @http.route('/count_extraccion_blanco', auth='public', type='http',methods=['POST'], csrf=False)
    def count_extraccion_blanco(self, desde = False, hasta = False, location=False):
        
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']
        company_obj = request.env['res.company'].search([('id','in',company_ids)],limit=1)

        domain=[('state','=','done'),('company_id', '=', company_ids)]
       
        if len(company_obj.extraccion_blanco.ids) > 0:
            domain.append(('move_raw_ids.product_id.id', 'in', company_obj.extraccion_blanco.ids))
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))

        mrp = mrp_production_obj.sudo().search(domain)
        
        total_principal = sum(mrp.move_raw_ids.filtered(lambda x: x.product_principal_id and (x.product_id.id in company_obj.extraccion_blanco.ids)).mapped('quantity_done'))
        total_finalizado = sum(mrp.mapped('product_qty'))
        
        if total_finalizado > 0 and total_principal > 0:
            return json.dumps(round(((total_finalizado/total_principal)*100),2))
        else:
            return json.dumps(0)


    @http.route('/count_extraccion_amarillo', auth='public', type='http',methods=['POST'], csrf=False)
    def count_extraccion_amarillo(self, desde = False, hasta = False, location=False):
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']        
        company_obj = request.env['res.company'].search([('id','in',company_ids)],limit=1)

        domain=[('state','=','done'),('company_id', '=', company_ids)]
       
        if len(company_obj.extraccion_amarillo.ids) > 0:
            domain.append(('move_raw_ids.product_id.id', 'in', company_obj.extraccion_amarillo.ids))
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))

        mrp = mrp_production_obj.sudo().search(domain)
        
        total_principal = sum(mrp.move_raw_ids.filtered(lambda x: x.product_principal_id and (x.product_id.id in company_obj.extraccion_amarillo.ids)).mapped('quantity_done'))
        total_finalizado = sum(mrp.mapped('product_qty'))
        
        if total_finalizado > 0 and total_principal > 0:
            return json.dumps(round(((total_finalizado/total_principal)*100),2))
        else:
            return json.dumps(0)

    @http.route('/count_empaque_primario', auth='public', type='http',methods=['POST'], csrf=False)
    def count_empaque_primario(self, desde = False, hasta = False, location=False):
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']
        domain=[
            ("move_raw_ids.emp_primary","=",True), 
            ("state","=","done"),
            ('company_id', 'in', company_ids),
            ]
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))
        mrp = mrp_production_obj.sudo().search(domain)
        total = sum(mrp.mapped('extraction_flour'))
        
        total_emp_primary = sum(mrp.move_raw_ids.filtered(lambda x: x.emp_primary).mapped('quantity_done'))
        total_producing = sum(mrp.mapped('qty_producing'))

        if total_emp_primary > 0:
            return json.dumps(round(((total_emp_primary/total_producing)*30000),2))
        else:
            return json.dumps(0)

    @http.route('/count_empaque_secundario', auth='public', type='http',methods=['POST'], csrf=False,)
    def count_empaque_secundario(self, desde = False, hasta = False, location=False):
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']
        domain=[
            ("move_raw_ids.emp_secondary","=",True),
            ("state","=","done"),
            ('company_id', 'in', company_ids),
            ]
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))
        mrp = mrp_production_obj.sudo().search(domain)
        total = sum(mrp.mapped('extraction_flour'))
        
        total_emp_secondary = sum(mrp.move_raw_ids.filtered(lambda x: x.emp_secondary).mapped('quantity_done'))
        total_producing = sum(mrp.mapped('qty_producing'))

        if total_emp_secondary > 0:
            return json.dumps(round(((total_emp_secondary/total_producing)*30000),2))
        else:
            return json.dumps(0)

    @http.route('/count_cinta_codificadora', auth='public', type='http',methods=['POST'], csrf=False)
    def count_cinta_codificadora(self, desde = False, hasta = False, location=False):
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']
        domain=[
            ("move_raw_ids.cinta_codificadora","=",True), 
            ("state","=","done"),
            ('company_id', 'in', company_ids),
            ]
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))
        mrp = mrp_production_obj.sudo().search(domain)
        total = sum(mrp.mapped('extraction_flour'))
        
        total_emp_secondary = sum(mrp.move_raw_ids.filtered(lambda x: x.cinta_codificadora).mapped('quantity_done'))
        total_producing = sum(mrp.mapped('qty_producing'))

        if total_emp_secondary > 0:
            return json.dumps(round(((total_emp_secondary/total_producing)*30000),2))
        else:
            return json.dumps(0)

    @http.route('/count_consumo_teflon', auth='public', type='http',methods=['POST'], csrf=False)
    def count_teflon(self, desde = False, hasta = False, location=False):
        company_ids = self._get_url(location)
        mrp_production_obj = request.env['mrp.production']
        domain=[
            ("move_raw_ids.teflon","=",True), 
            ("state","=","done"),
            ('company_id', 'in', company_ids),
            ]
        if desde:
            domain.append(('date_finished', '>=', desde))
        if hasta:
            domain.append(('date_finished', '<=', hasta))
        mrp = mrp_production_obj.sudo().search(domain)
        total = sum(mrp.mapped('extraction_flour'))
        
        total_emp_secondary = sum(mrp.move_raw_ids.filtered(lambda x: x.teflon).mapped('quantity_done'))
        total_producing = sum(mrp.mapped('qty_producing'))

        if total_emp_secondary > 0:
            return json.dumps(round(((total_emp_secondary/total_producing)*30000),2))
        else:
            return json.dumps(0)
