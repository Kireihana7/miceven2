# -*- coding: utf-8 -*-
#codigo modificado por :
#eliomeza1@gmail.com

import logging
from odoo import api, fields, models, _ 
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('__name__')




class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    tipo_factura = fields.Selection(related="move_id.move_type",string="Tipo de Factura")
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict',store=True)
    partner_id_comany = fields.Many2one(related="move_id.company_id.partner_id",string="Campo Partner")
    concept_id_partner = fields.Many2one('muni.wh.concept.partner',string='Municipal Tax',domain="[('partner_id', '=', partner_id)]")
    concept_id_partner2 = fields.Many2one('muni.wh.concept',string='Municipal Tax')
    concept_id = fields.Many2one('muni.wh.concept',string='Municipal Tax')
    move_type = fields.Selection(related="move_id.move_type",)

    @api.onchange('concept_id_partner')
    def _compute_concept_id_partner(self):
            for rec in self:
                if rec.tipo_factura in ('in_invoice','in_refund') and rec.concept_id_partner:
                    rec.concept_id = rec.concept_id_partner.muni_concept.id
                   
    @api.onchange('concept_id_partner2')
    def _compute_concept_id_partner2(self):
        for rec in self:
            if rec.tipo_factura in ('out_invoice','out_refund') and rec.concept_id_partner2:
                rec.concept_id = rec.concept_id_partner2

class AccountMove(models.Model):
    _inherit = 'account.move'

    wh_muni_id = fields.Many2one('municipality.tax', string='Withholding municipal tax', readonly=True, copy=False)

    def _create_muni_wh_voucher(self):
        vals = {}
        values = {}
        muni_wh = self.env['municipality.tax']
        muni_wh_line = self.env['account.move.line']
        res = []
        aliquot_new = 0
        porcentaje_alic = 0
        for item in self.invoice_line_ids:
            base_impuesto=item.price_subtotal if item.currency_id == item.company_id.currency_id else item.price_subtotal_ref
            impuesto_mun=item.concept_id.aliquot
            if not item.move_id.partner_id.partner_type:
                raise UserError('Debe configurar en el contacto el tipo de Proveedor y/o Cliente')
            if item.move_id.partner_id.partner_type == 'D':
                porcentaje_alic = '50'
                aliquot_new = (impuesto_mun*50)/100
            if item.move_id.partner_id.partner_type == 'T':
                porcentaje_alic = '100'
                aliquot_new = impuesto_mun
            if item.concept_id.aliquot>0:
                res.append((0,0, {
                    'code': item.concept_id.code,
                    'aliquot': aliquot_new,
                    'porcentaje_alic': porcentaje_alic,
                    'concept_id': item.concept_id.id,
                    'concept_partner': item.concept_id_partner.id if item.concept_id_partner else False,
                    'concept_partner2': item.concept_id_partner2.id if item.concept_id_partner2 else False,
                    'alicuota_normal' : item.concept_id.aliquot,
                    'base_tax': base_impuesto, 
                    'invoice_id': self.id,
                    'invoice_date' : self.date,
                    'vendor_invoice_number': self.vendor_invoice_number,
                    'invoice_ctrl_number': self.nro_control,
                }))
        vals = {
           'partner_id': self.partner_id.id,
           'rif': self.partner_id.vat,
           'move_type': self.move_type,
           'invoice_id': self.id,
           'act_code_ids': res,
           'move_type':self.move_type,
           'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
        }
        muni_tax = muni_wh.create(vals)
        self.write({'wh_muni_id': muni_tax.id})

    def actualiza_voucher_wh(self):
        cursor_municipality = self.env['municipality.tax'].search([('id','=',self.wh_muni_id.id)])
        cursor_municipality_line = self.env['municipality.tax.line'].search([('municipality_tax_id','=',self.wh_muni_id.id)])
        for borrar in cursor_municipality_line:
            borrar.unlink()
        res = []
        aliquot_new = 0
        porcentaje_alic = 0
        for item in self.invoice_line_ids:
            base_impuesto=item.price_subtotal if item.currency_id == item.company_id.currency_id else item.price_subtotal_ref
            impuesto_mun=item.concept_id.aliquot
            if not item.move_id.partner_id.partner_type:
                raise UserError('Debe configurar en el contacto el tipo de Proveedor y/o Cliente')
            if item.move_id.partner_id.partner_type == 'D':
                porcentaje_alic = '50'
                aliquot_new = (impuesto_mun*50)/100
            if item.move_id.partner_id.partner_type == 'T':
                porcentaje_alic = '100'
                aliquot_new = impuesto_mun
            if item.concept_id.aliquot>0:
                res.append((0,0, {
                    'code': item.concept_id.code,
                    'aliquot': aliquot_new,
                    'alicuota_normal' : item.concept_id.aliquot,
                    'porcentaje_alic': porcentaje_alic,
                    'concept_id': item.concept_id.id,
                    'concept_partner': item.concept_id_partner.id if item.concept_id_partner else False,
                    'concept_partner2': item.concept_id_partner2.id if item.concept_id_partner2 else False,
                    'base_tax': base_impuesto,
                    'invoice_id': self.id,
                    'invoice_date' : self.date,
                    'vendor_invoice_number': self.vendor_invoice_number,
                    'invoice_ctrl_number': self.nro_control,
                    'move_type': 'dont_apply',
                }))
        for det in cursor_municipality:
            self.env['municipality.tax'].browse(det.id).write({
                'move_type': self.move_type,
                'partner_id': self.partner_id.id,
                'rif': self.partner_id.vat,
                'invoice_id': self.id,
                'act_code_ids': res,
                'manual_currency_exchange_rate':self.manual_currency_exchange_rate,
                })


    def action_post(self):
        """This function create municital retention voucher too."""
        invoice = super().action_post()
        # es agente de retencion municipal
        for rec in self:
            if rec.partner_id.muni_wh_agent or rec.company_id.partner_id.muni_wh_agent:
                # si no existe una retencion ya
                bann=0
                bann=rec.verifica_exento_muni()
                if bann>0:
                    if not rec.wh_muni_id:
                        rec._create_muni_wh_voucher()
                    if rec.wh_muni_id:
                        rec.actualiza_voucher_wh()
                        rec.unifica_alicuota_iguales()
        return invoice

    def button_draft(self):
        '''
        Este metodo se usa para pasar las retenciones a borrador cuando se pasa la factura de publicado a borrador (IAE)
        :return:
        '''
        for hw in self:
            if hw.wh_muni_id.state == 'posted':
                hw.wh_muni_id.write({
                'state': 'draft',
                })
            if hw.wh_muni_id and hw.wh_muni_id.asiento_post and hw.wh_muni_id.state == 'posted':
                hw.wh_muni_id.asiento_post.button_draft()
        return super(AccountMove, self).button_draft()

    def verifica_exento_muni(self):
        acum=0
        puntero_move_line = self.env['account.move.line'].search([('move_id','=',self.id)])
        for det_puntero in puntero_move_line:
            acum=acum+det_puntero.concept_id.aliquot
        return acum


    def unifica_alicuota_iguales(self):
        lista_impuesto = self.env['muni.wh.concept'].search([])
        for det_tax in lista_impuesto:
            lista_mov_line = self.env['municipality.tax.line'].search([('invoice_id','=',self.id),('concept_id','=',det_tax.id)])
            base_tax=0
            wh_amount=0
            if lista_mov_line:
                for det_mov_line in lista_mov_line:                
                    base_tax=base_tax+det_mov_line.base_tax
                    wh_amount=wh_amount+det_mov_line.wh_amount
                    code=det_mov_line.code
                    aliquot=det_mov_line.aliquot
                    invoice_id=det_mov_line.invoice_id.id
                    vendor_invoice_number=det_mov_line.vendor_invoice_number
                    municipality_tax_id=det_mov_line.municipality_tax_id.id
                    invoice_ctrl_number=det_mov_line.invoice_ctrl_number
                    tipe='purchase'
                    concept_id=det_mov_line.concept_id.id
                lista_mov_line.unlink()
                move_obj = self.env['municipality.tax.line']
                valor={
                'code':code,
                'aliquot':aliquot,
                'invoice_id':invoice_id,
                'vendor_invoice_number':vendor_invoice_number,
                'municipality_tax_id':municipality_tax_id,
                'invoice_ctrl_number':invoice_ctrl_number,
                'base_tax':base_tax,
                'wh_amount':wh_amount,
                'move_type':'purchase',
                'concept_id':concept_id,
                }
                move_obj.create(valor)
