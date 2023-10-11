# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime

class AccountsReceivableWizardReport(models.TransientModel):
    _name = 'report.accounts.receivable.product'
    _description = ''

    from_date = fields.Date(string="Desde")
    to_date = fields.Date(string="Hasta")
    invoice_user_id = fields.Many2one('res.users', string='Vendedor')

    def print_report(self):
        datas = []
        invoice_lines = []

        if self.to_date < self.from_date:
                raise ValidationError(_("La fecha Desde no puede ser menor a la fecha Hasta."))
        

        sql_account_move = f'''
            SELECT id, partner_id, invoice_date, name, currency_id, amount_total, amount_residual, invoice_date_due, invoice_user_id
            FROM account_move 

            WHERE invoice_date >= '{self.from_date}'
            AND invoice_date <= '{self.to_date}'
            AND invoice_user_id = '{self.invoice_user_id.id}'
            AND amount_residual > 0
        '''
        self._cr.execute(sql_account_move)
        account_moves = self._cr.dictfetchall()

        if len(account_moves) == 0:
            raise ValidationError(_('No se encontraron registros.'))
        
        else:
            for invoice in account_moves:
                id = invoice['id']
                # SQL a la tabla 'account.move.line':
                sql_account_move_line = f'''
                    SELECT 
                    
                    account_move_line.id, 
                    account_move_line.product_id, 
                    account_move_line.quantity, 
                    account_move_line.price_unit, 
                    account_move_line.price_subtotal,
                    account_move_line.product_uom_id

                    FROM account_move_line
                    
                    LEFT JOIN product_product ON product_product.id = account_move_line.product_id
                    LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                    LEFT JOIN product_category ON product_category.id = product_template.categ_id

                    WHERE account_move_line.move_id = \''''+str(id)+'''\'
                    AND product_category.complete_name LIKE '%PRODUCTO TERMINADO%'
                '''
                self._cr.execute(sql_account_move_line)
                invoice_line_ids = self._cr.dictfetchall()
                if len(invoice_line_ids) > 0:
                    for line in invoice_line_ids:
                        cliente_id = invoice['partner_id']
                        product_id = line['product_id']
                        product_uom = line['product_uom_id']
                        
                        if cliente_id is not None and product_id is not None:
                            # ================ Cliente ================ #
                            # SQL para la tabla 'partner_id'
                            sql_partner_cliente = f'''
                                SELECT * 
                                FROM res_partner
                                WHERE id = \''''+str(cliente_id)+'''\'
                            '''
                            # Ejecutando:
                            self._cr.execute(sql_partner_cliente)
                            res_partner_cliente = self._cr.dictfetchall()

                            # ================ Unidad de medida ================ #
                            # SQL para la tabla 'uom_uom'
                            sql_product_uom = f'''
                                SELECT name
                                FROM uom_uom
                                WHERE id = \''''+str(product_uom)+'''\'
                            '''
                            # Ejecutando:
                            self._cr.execute(sql_product_uom)
                            dict_product_uom = self._cr.dictfetchall()
                            # ================ Dias transcurridos ================ #

                            date_invoice = invoice['invoice_date']
                            date_actually = date.today()
                            days = date_actually - date_invoice
                            

                            # ================ Vendedor ================ #
                            nombre_vendedor = ''
                            if 'invoice_user_id' in invoice:
                                if invoice['invoice_user_id'] is not None:
                                    invoice_user = invoice['invoice_user_id']                
                                    # SQL para la tabla 'res_users'
                                    sql_vendedor = f'''
                                        SELECT res_partner.name as vendedor
                                        FROM res_users
                                        LEFT JOIN res_partner ON res_partner.id = res_users.partner_id
                                        WHERE res_users.id = \''''+str(invoice_user)+'''\'
                                    '''
                                    # Ejecutando:
                                    self._cr.execute(sql_vendedor)
                                    res_invoice_user_id = self._cr.dictfetchall()
                                    if len(res_invoice_user_id) > 0:
                                        nombre_vendedor = res_invoice_user_id[0]['vendedor']

                            # ================ Producto ================ #
                            # SQL para la tabla 'product.product'
                            sql_product_product = f'''
                                SELECT 

                                product_product.id,
                                product_product.product_tmpl_id,
                                product_category.complete_name,  
                                product_template.name AS product_name

                                FROM product_product
                                
                                LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                LEFT JOIN product_category ON product_category.id = product_template.categ_id

                                WHERE product_product.id = \''''+str(product_id)+'''\'
                            '''
                            # Ejecutando:
                            self._cr.execute(sql_product_product)
                            res_product = self._cr.dictfetchall()
                            
                            # raise ValidationError(_(dict_product_uom))

                            if product_id is not None and res_product[0]['product_tmpl_id'] is not None:
                                invoice_lines.append({
                                    'id': line['id'],
                                    'invoice_date': invoice['invoice_date'].strftime("%d/%m/%Y") if invoice['invoice_date'] else '',
                                    'invoice_date_due': invoice['invoice_date_due'].strftime("%d/%m/%Y"),
                                    'partner_id': res_partner_cliente[0]['name'].upper() if cliente_id is not None else '',
                                    #'UOM': dict_product_uom[0]['name']['es_VE'].upper() if len(dict_product_uom) == 1 and dict_product_uom[0]['name'] is not None else '',
                                    'UOM': dict_product_uom[0]['name'].upper() if len(dict_product_uom) == 1 and dict_product_uom[0]['name'] is not None else '',
                                    'city_id': res_partner_cliente[0]['city'] if res_partner_cliente[0]['city'] else '',
                                    #'vendor_id': line.vendor_id.name if line.vendor_id else '',
                                    'invoice_user_id': nombre_vendedor,
                                    'days': days.days,
                                    'name': invoice['name'],
                                    'cantidad_x_fardo': line['quantity'],
                                    'precio_x_fardo_usd': line['price_unit'],
                                    'monto_total_usd': line['price_subtotal'],
                                    'saldo_abonado': False,
                                    'pendiente_x_cancelar': False,
                                    'product': res_product[0]['product_name'].upper() if product_id is not None else '',
                                    #'product': 'producto de prueba',
                                    'company_currency_id': invoice['currency_id'],
                                })                              
                    
                    # Agregando Saldo Abonado y Pendiente por cancelar a la primera línea:
                    if len(invoice_lines) > 0:
                        current_invoice_lines  = []
                        for i in invoice_lines:
                            if i['name'] == invoice['name']:
                                current_invoice_lines.append(i)
                       
                        saldo_abonado = invoice['amount_total'] - invoice['amount_residual']
                        if len(current_invoice_lines) > 0:
                            current_invoice_lines[0]['saldo_abonado'] = saldo_abonado
                            current_invoice_lines[0]['pendiente_x_cancelar'] = invoice['amount_residual']

            if len(invoice_lines) == 0:
                raise ValidationError(_('No se encontraron registros.'))

            total_cantidad_fardos = 0
            total_a_cancelar = 0
            total_saldo_abonado = 0
            total_pendiente_x_cancelar = 0

            if len(invoice_lines) > 0:
                for line in invoice_lines:
                    total_cantidad_fardos += line['cantidad_x_fardo']
                    total_a_cancelar += line['monto_total_usd']
                    if line['saldo_abonado']:
                        total_saldo_abonado += line['saldo_abonado']

                total_pendiente_x_cancelar = total_a_cancelar - total_saldo_abonado

            # raise ValidationError(_(f'Currency: {invoice_lines[0]["company_currency_id"]}'))
            datas.append({
                'company_currency_id': invoice_lines[0]["company_currency_id"],
                'invoice_lines': invoice_lines,
                'total_cantidad_fardos': total_cantidad_fardos,
                'total_a_cancelar': total_a_cancelar,
                'total_saldo_abonado': total_saldo_abonado,
                'total_pendiente_x_cancelar': total_pendiente_x_cancelar      
            }) 

            res = {
                'documents': datas,
                'start_date': self.from_date.strftime("%d/%m/%Y"),
                'end_date': self.to_date.strftime("%d/%m/%Y"),                
            }
            
            data = {
                'form': res
            }
            
            return self.env.ref('eu_report_accounts_receivable_product.report_list_accounts_receivable_product').report_action(self, data=data)