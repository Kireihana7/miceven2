# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime

class ShPurchaseAgreement(models.Model):
    _inherit = 'purchase.agreement'
    
    sh_purchase_agreement_agriculture_line_ids = fields.One2many('purchase.agreement.line', 'agreement_id', string='Purchase Agreement Line (Agriculture)')
    agriculture_company = fields.Boolean(related='company_id.agriculture_company')

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisiciones',
        copy=False,
        tracking=True
    )

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )      

    # crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=True, tracking=True)
    # Este campo no debe estar aquí:
    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)    

    def action_confirm_auto(self):
        for rec in self:
            # Si no se trata de una empresa agrícola, que ejecute su funcionamiento por defecto:
            if rec.company_id.agriculture_company == False:
                super(ShPurchaseAgreement, self).action_confirm_auto()
            else:
                # Versión agrícola:
                if len(rec.partner_ids) == 0:
                    raise UserError('Debe añadir al menos un Proveedor')
                for partner in rec.partner_ids:
                    if not rec.sh_agreement_type:
                        raise UserError('Seleccione el Tipo de Concurso')
                    line_ids = []
                    current_date = None
                    if rec.sh_delivery_date:
                        current_date = rec.sh_delivery_date
                    else:
                        current_date = fields.Datetime.now()
                        
                    purchase_order_obj = self.env['purchase.order']
                    purchase_order_obj = purchase_order_obj.create({
                        'partner_id': partner.id,
                        'date_order': datetime.now(),
                        'origin': rec.sh_source,
                        'agreement_id':rec.id,
                        'user_id': rec.sh_purchase_user_id.id,
                        'company_id':rec.company_id.id,
                        'picking_type_id':self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', rec.company_id.id)],limit=1).id
                    })
                    
                    for rec_line in rec.sh_purchase_agreement_line_ids:
                        purchase_product_matrix_module = self.env['ir.module.module'].sudo().search([('name','=','purchase_product_matrix'),('state','=','installed')],limit=1)
                        
                        crop_request_transaction_id = rec_line.crop_request_transaction_id.id
                        crop_request_transaction_line_id = rec_line.crop_request_transaction_line_id

                        transaction_obj = self.env['crop.request.transaction'].search([('id', '=', crop_request_transaction_id)])
                        type = transaction_obj.type

                        # transacion_model = ''
                        # transacion_model_id = ''

                        # price_unit = 0
                        # price_subtotal = 0

                        # if type == 'equipment_reservation':                
                        #     equipment_reservation_id = transaction_obj.equipment_reservation_id.id
                        #     transacion_model = 'equipment.reservation'
                        #     transacion_model_id = equipment_reservation_id
                        #     # Línea:
                        #     price_unit = self.env['equipment.reservation.lines'].search([('id', '=', crop_request_transaction_line_id)]).price
                        #     price_subtotal = self.env['equipment.reservation.lines'].search([('id', '=', crop_request_transaction_line_id)]).price_subtotal

                        # if type == 'labour_management':
                        #     labour_management_id = transaction_obj.labour_management_id.id
                        #     transacion_model = 'labour.management'
                        #     transacion_model_id = labour_management_id             
                        #     # price_unit = 0
                        #     price_subtotal = self.env[transacion_model].search([('id', '=', transacion_model_id)]).total_pay_amount
                        #     price_unit = price_subtotal

                        # if type == 'crop_material_management':
                        #     crop_material_id = transaction_obj.crop_material_id.id
                        #     transacion_model = 'crop.material.management'
                        #     transacion_model_id = crop_material_id     
                        #     # Línea:
                        #     price_unit = self.env['crop.material.management.lines'].search([('id', '=', crop_request_transaction_line_id)]).price
                        #     price_subtotal = self.env['crop.material.management.lines'].search([('id', '=', crop_request_transaction_line_id)]).price_subtotal  

                        price_unit = rec_line.sh_price_unit
                        # price_subtotal = 0

                        if purchase_product_matrix_module:
                            line_vals={
                                'product_id':rec_line.sh_product_id.id,
                                'name':rec_line.sh_product_id.name_get()[0][1],
                                'product_template_id':rec_line.sh_product_id.product_tmpl_id.id,
                                'date_planned':current_date,
                                'product_qty':rec_line.sh_qty,
                                'status':'draft',
                                'agreement_id':rec.id,
                                'product_uom':rec_line.sh_product_id.uom_id.id,
                                'price_unit': price_unit,
                                # 'price_subtotal_ref': price_subtotal,
                                'account_analytic_id': rec_line.account_analytic_id.id,
                                'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                                # ================ New Fields ================ #
                                'farmer_request_id': rec_line.farmer_request_id.id,
                                'crop_request_transaction_id' : rec_line.crop_request_transaction_id.id,
                                'crop_request_transaction_line_id' : rec_line.crop_request_transaction_line_id,                            
                                'analytic_account_id_1' : rec_line.analytic_account_id_1.id,
                                'analytic_account_id_2' : rec_line.analytic_account_id_2.id,
                                'analytic_account_id_3' : rec_line.analytic_account_id_3.id,
                                'analytic_account_id_4' : rec_line.analytic_account_id_4.id                              
                            }
                        else:
                            line_vals={
                                'product_id':rec_line.sh_product_id.id,
                                'name':rec_line.sh_product_id.name_get()[0][1],
                                'date_planned':current_date,
                                'product_qty':rec_line.sh_qty,
                                'status':'draft',
                                'agreement_id':rec.id,
                                'product_uom':rec_line.sh_product_id.uom_id.id,
                                'price_unit': price_unit,
                                # 'price_subtotal_ref': price_subtotal,
                                'account_analytic_id': rec_line.account_analytic_id.id,
                                'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                                # ================ New Fields ================ #
                                'farmer_request_id': rec_line.farmer_request_id.id,
                                'crop_request_transaction_id' : rec_line.crop_request_transaction_id.id,
                                'crop_request_transaction_line_id' : rec_line.crop_request_transaction_line_id,                            
                                'analytic_account_id_1' : rec_line.analytic_account_id_1.id,
                                'analytic_account_id_2' : rec_line.analytic_account_id_2.id,
                                'analytic_account_id_3' : rec_line.analytic_account_id_3.id,
                                'analytic_account_id_4' : rec_line.analytic_account_id_4.id                               
                            }
                        line_ids.append((0,0,line_vals))
                    purchase_order_obj.order_line_agriculture = line_ids
                    purchase_order_obj.onchange_partner_id()
                    purchase_order_obj.order_line_agriculture._compute_tax_id()
                    rec.state ='confirm'

class ShPurchaseAgreementLine(models.Model):
    _inherit = 'purchase.agreement.line'

    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Línea de Requisiciones',
        copy=False,
        tracking=True
    )

    sh_product_id = fields.Many2one('product.product','Product',required=True)

    product_tmpl_id = fields.Many2one(
        related='sh_product_id.product_tmpl_id',
        string='Product Template ID',
        required=True,
        tracking=True
    )

    sh_product_type = fields.Selection(
        related='product_tmpl_id.type',
        string='Type',
        required=True,
        tracking=True
    )   

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    )

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        readonly=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )        

    # crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=True, tracking=True)
    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)