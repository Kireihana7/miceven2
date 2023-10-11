# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

import odoo
from odoo import http
from odoo import fields
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime



class AccountPaymentTxt(http.Controller):
  
        
    @http.route('/paymentTXTreports/<int:TXTpayment>', type='http', auth="public", website=True, multilang=False)
    def report_txt_massive(self,TXTpayment,**kwargs):
        headers = [('Content-Type', 'text/plain')]
        id_payment_txt_obj = request.env['account.batch.payment']
        id_payment_txt = id_payment_txt_obj.sudo().search([('id','=', TXTpayment)])
        content,nombre_archivo =id_payment_txt_obj.act_getfile(id_payment_txt,)
        txt = base64.b64decode(content)
        headers.append(('Content-Length', len(txt)))
        response = request.make_response(txt, headers)
        response.headers.add('Content-Disposition', 'attachment; filename=%s;' % nombre_archivo)
        return response

    @http.route('/paymentTXTreports_ingre/<int:TXTpayment>', type='http', auth="public", website=True, multilang=False)
    def report_txt_massive_bene(self,TXTpayment,**kwargs):
        headers = [('Content-Type', 'text/plain')]
        id_payment_txt_obj = request.env['account.batch.payment']
        id_payment_txt = id_payment_txt_obj.sudo().search([('id','=', TXTpayment)])
        content = id_payment_txt_obj.act_getfile_bene(id_payment_txt,)
        txt = base64.b64decode(content)
        headers.append(('Content-Length', len(txt)))
        response = request.make_response(txt, headers)
        #fecha_hoy = datetime.now().strftime("%Y%m%d%H%M%S")
        #nombre_archivo = 'BENEFICIARIO.txt;'
        response.headers.add('Content-Disposition', 'attachment; filename=BENEFICIARIO.txt;') 
        return response