# -*- coding: utf-8 -*-
# Jose Ñeri - 4
from odoo import models, fields, api
from odoo.tools.misc import formatLang
from datetime import date, datetime, timedelta

class WizardMicevenPagoBalance(models.TransientModel):
    _name = 'wizard.miceven.pago.balance'

    def get_default_fecha(self):
        return self.env['account.move'].search([('id','=',self._context.get('active_id'))]).invoice_date

    desde=fields.Date('Desde',required=True,default=get_default_fecha)
    
    hasta=fields.Date('Hasta',required=True,default=get_default_fecha)
    
    def get_default_typo(self):
        return self.env['account.move'].search([('id','=',self._context.get('active_id'))]).move_type
    motype=fields.Selection([('out_invoice','Factura Cliente'),('out_refund','Factura Rectificativa Cliente'),
                            ('in_invoice','Factura Proveedor'),('in_refund','Factura Rectificativa Proveedor'),
                            ('out_receipt','Recibo de ventas'),('in_receipt','Recibo de compra'),],'Tipo de Factura',required=True,default=get_default_typo)
    
    def get_default_factura(self):
        return self.env['account.move'].search([('id','=',self._context.get('active_id'))])
    invoice_id=fields.Many2one('account.move',string="Factura a revisar",default=get_default_factura)

    def print_report_balance(self):
        return self.env.ref('eu_account_reports.action_balance_payment_miceven').report_action(self)