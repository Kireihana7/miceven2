# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    vendor_invoice_number = fields.Char(string='Nro factura proveedor',
        copy=False,
        help='El número de factura generado por el proveedor' )
    nro_control = fields.Char(string='Nro de Control',
        copy=False,
        help='Nro de control de la factura de proveedor', required=False)
    transaction_type = fields.Selection(([('01-reg','Registro'),
                                          ('02-complemento', 'Complemento'),
                                          ('03-anulacion', 'Anulación'),
                                          ('04-ajuste', 'Ajuste')]), string='Transaction Type', readonly=False,
                                            states={'draft': [('readonly', False)]},
                                            help='This is transaction type', compute='_compute_transaction_type')
    ajust_date = fields.Date(string='Fecha de Ajuste',readonly=False,
                                            states={'draft': [('readonly', False)]})
    
    deductible  =   fields.Boolean('¿No Deducible?')

    @api.depends('move_type', 'state')
    def _compute_transaction_type(self):
        for move in self:
            if move.move_type in ('out_refund','in_refund') and move.state != 'cancel':
                move.transaction_type = '02-complemento'
            elif move.state == 'cancel':
                move.transaction_type = '03-anulacion'
            elif move.debit_origin_id.id != False:
                move.transaction_type = '02-complemento'
            else:
                move.transaction_type = '01-reg'

#    @api.constrains('nro_control')
#    def _check_control_number(self):
#        records = self.env['account.move']
#        if self.nro_control:
#            invoice_exist = records.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('out_refund','out_invoice')),('account_serie','=',self.account_serie.id)])
#            if invoice_exist > 0 and self.move_type in ('out_refund','out_invoice'):
#                raise ValidationError(("Ya existe una factura con este Número de Control"))
#            if self.vendor_invoice_number:
#                invoice_exist = records.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('in_refund','in_invoice')),('partner_id','=',self.partner_id.id),('vendor_invoice_number','=',self.vendor_invoice_number),('state','!=','cancel')])
#                if invoice_exist > 0 and self.move_type in ('in_refund','in_invoice'):
#                    raise ValidationError(("Ya existe una factura con este Número de Control"))
#            return True

    # def write(self,vals):
    #     res = super(AccountInvoice, self).write(vals)
    #     if self.nro_control:
    #         if self.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('out_refund','out_invoice'))]) > 0:
    #             raise ValidationError(("Ya existe una factura con este Número de Control"))
    #         if self.vendor_invoice_number:
    #             if self.search_count([('nro_control', '=', self.nro_control),('id', '!=', self.id),('move_type','in',('in_refund','in_invoice')),('partner_id','=',self.partner_id.id),('vendor_invoice_number','=',self.vendor_invoice_number),('state','!=','cancel')]) > 0:
    #                 raise ValidationError(("Ya existe una factura con este Número de Control"))
    #     return res

    # def action_post(self):
    #     for rec in self:
    #         if not rec.nro_control and rec.move_type != 'entry':
    #             raise UserError('Debe asignarle un número de control a la factura antes de publicarla')
    #     res = super(AccountInvoice, self).action_post()
    #     return res
