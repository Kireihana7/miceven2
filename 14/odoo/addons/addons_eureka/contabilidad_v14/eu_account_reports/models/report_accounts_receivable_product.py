# -*- coding: utf-8 -*-
# Manuel Jimenez - 2
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime

class AccountsReceivableWizardReport(models.TransientModel):
    _name = 'report.accounts.receivable.product'
    _description = 'Cuentas por cobrar producto terminado'

    from_date = fields.Date(string="Fecha Desde:")
    to_date = fields.Date(string="Fecha Hasta:")
    order = fields.Selection([('ASC', 'Ascendente'), ('DESC', 'Descendente')], default='ASC', string="Ordenar por fecha:") 
    invoice_user_ids = fields.Many2many('res.users', string='Vendedor:')
    partner_zone_ids = fields.Many2many('res.partner.zones', string='Zona')
    # UPDATE:
    partner_ids = fields.Many2many('res.partner', string='Cliente')
    product_ids = fields.Many2many("product.product", string="Producto", domain=[('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO')])
    invoice_ids = fields.Many2many("account.move", string="Factura")

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    company_currency_id = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_id.id,string="Moneda de la Compañía")

    def print_report(self):
        datas = []
        invoices = []

        # Validación de fechas:
        if self.from_date > self.to_date:
            raise ValidationError(_('La fecha de inicio no puede ser mayor a la fecha fin.'))

        param_user_ids = ''
        param_zones = ''
        mis_ids     = ','.join([str(i) for i in self.invoice_user_ids.ids])
        mis_zones   = ','.join([str(i) for i in self.partner_zone_ids.ids])

        if self.invoice_user_ids:
            param_user_ids = f'AND account_move.invoice_user_id in ({mis_ids})'
        if self.partner_zone_ids:
            param_zones = f'AND account_move.partner_zone in ({mis_zones})'

        # Cliente:
        param_partner_ids = '1 = 1'
        my_partner_ids = ','.join([str(i) for i in self.partner_ids.ids])
        if self.partner_ids:
            param_partner_ids = f'account_move.partner_id in ({my_partner_ids})'

        # Producto:
        param_product_ids = "product_category.complete_name LIKE '%PRODUCTO TERMINADO%'"
        my_product_ids = ','.join([str(i) for i in self.product_ids.ids])
        if self.product_ids:
            param_product_ids = f'product_product.id in ({my_product_ids})'

        # Factura:
        param_invoice_ids = '1 = 1'
        my_invoice_ids = ','.join([str(i) for i in self.invoice_ids.ids])
        if self.invoice_ids:
            param_invoice_ids = f'account_move.id in ({my_invoice_ids})'

        sql_account_move = f'''
            SELECT 

            account_move.id, 
            account_move.partner_id, 
            account_move.invoice_date, 
            account_move.name, 
            account_move.currency_id, 
            account_move.amount_total,
            account_move.amount_ref, 
            account_move.amount_residual, 
            account_move.amount_residual_signed_ref, 
            account_move.invoice_date_due, 
            account_move.invoice_user_id,
            res_partner_zones.name as zone

            FROM account_move 

            LEFT JOIN account_journal ON account_journal.id = account_move.journal_id
            LEFT JOIN res_partner ON res_partner.id = account_move.partner_id
            LEFT JOIN res_partner_zones ON res_partner_zones.id = res_partner.partner_zone

            WHERE

            account_move.move_type = 'out_invoice'
            
            -- Vendedor:
            {param_user_ids}
            
            -- Zona:
            {param_zones}

            -- Cliente:
            AND {param_partner_ids}
            -- Factura:
            AND {param_invoice_ids}   

            AND account_move.invoice_date >= '{self.from_date}'
            AND account_move.invoice_date <= '{self.to_date}'
            AND account_move.company_id = '{self.company_id.id}'
            
            AND account_move.state = 'posted'
            AND account_journal.name NOT LIKE '%PROMO%'
            AND account_move.amount_residual != 0    
            

            ORDER BY account_move.invoice_date {self.order}
        '''
        # raise UserError(sql_account_move)
        self._cr.execute(sql_account_move)
        account_moves = self._cr.dictfetchall()

        if len(account_moves) == 0:
            raise ValidationError(_('No se encontraron registros.'))
        
        else:
            lista_vendedores = []
            for invoice in account_moves:
                invoice_lines = []
                id = invoice['id']

                # Moneda de la factura:
                invoice_currency_id = invoice['currency_id']
                
                field_amount_total = invoice['amount_total'] # Total a Pagar
                field_amount_residual = invoice['amount_residual'] # Monto Adeudado
                field_amount_abonado= field_amount_total - field_amount_residual

                if self.company_currency_id.id != invoice_currency_id:

                    field_amount_total = invoice['amount_ref']
                    field_amount_residual = invoice['amount_residual_signed_ref']
                    field_amount_abonado= field_amount_total - field_amount_residual

                # ================ Cliente ================ #
                cliente_id = invoice['partner_id']
                # SQL para la tabla 'partner_id'
                sql_partner_cliente = f'''
                    SELECT * 
                    FROM res_partner
                    WHERE id = \''''+str(cliente_id)+'''\'
                '''
                # Ejecutando:
                self._cr.execute(sql_partner_cliente)
                res_partner_cliente = self._cr.dictfetchall()
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
                            lista_vendedores.append(nombre_vendedor)
                            
                # ================ Dias transcurridos ================ #
                    date_invoice = invoice['invoice_date']
                    date_actually = date.today()
                    days = date_actually - date_invoice

                if field_amount_total > 0:
                    # SQL a la tabla 'account.move.line':
                    sql_account_move_line = f'''
                        SELECT 
                        
                        account_move_line.id, 
                        account_move_line.product_id, 
                        account_move_line.quantity, 
                        account_move_line.price_unit,
                        account_move_line.price_unit_ref, 
                        account_move_line.price_subtotal,
                        account_move_line.price_subtotal_ref,
                        account_move_line.product_uom_id
                        
                        FROM account_move_line
                        
                        LEFT JOIN product_product ON product_product.id = account_move_line.product_id
                        LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                        LEFT JOIN product_category ON product_category.id = product_template.categ_id

                        WHERE account_move_line.move_id = {str(id)}
                        AND {param_product_ids}
                    '''
                    self._cr.execute(sql_account_move_line)
                    invoice_line_ids = self._cr.dictfetchall()
                    if len(invoice_line_ids) > 0:
                        for line in invoice_line_ids:
                            product_id = line['product_id']
                            product_uom = line['product_uom_id']
                            
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
                            
                            # ================ Unidad de Medida ================ #
                            # SQL para la tabla 'uom_uom'
                            product_uom_name = ''
                            if product_uom is not None:
                                sql_uom_uom = f'''
                                    SELECT name 
                                    FROM uom_uom
                                    WHERE id = \''''+str(product_uom)+'''\'
                                '''
                                # Ejecutando:
                                self._cr.execute(sql_uom_uom)
                                res_uom_uom = self._cr.dictfetchall()
                                if len(res_uom_uom) > 0:
                                    product_uom_name = res_uom_uom[0]['name']                                

                            if product_id is not None and res_product[0]['product_tmpl_id'] is not None:
                                invoice_lines.append({
                                    'id': line['id'],
                                    'cantidad_x_fardo': line['quantity'],
                                    'precio_x_fardo_usd': line['price_unit'] if invoice["currency_id"] == self.company_currency_id.id else line['price_unit_ref'],
                                    'sub_total_usd': line['price_subtotal'] if invoice["currency_id"] == self.company_currency_id.id else line['price_subtotal_ref'],
                                    'product': res_product[0]['product_name'].upper() if product_id is not None else '',
                                    # 'product': 'aaa',
                                    'product_uom_name': product_uom_name,
                                    # 'product_uom_name': 'bbb',
                                })
                        
                    # Agregando Saldo Abonado y Pendiente por cancelar a la primera línea:
                    if len(invoice_lines) > 0:
                        invoices.append({
                            'invoice_date': invoice['invoice_date'].strftime("%d/%m/%Y") if invoice['invoice_date'] else '',
                            'invoice_date_due': invoice['invoice_date_due'].strftime("%d/%m/%Y"),
                            'partner_id': res_partner_cliente[0]['name'].upper() if cliente_id is not None else '',
                            'city_id': res_partner_cliente[0]['city'] if res_partner_cliente[0]['city'] else '',
                            'invoice_user_id': nombre_vendedor,
                            'name': invoice['name'],
                            'days': days.days,
                            'field_amount_total': field_amount_total,
                            'saldo_abonado': field_amount_abonado,
                            'pendiente_x_cancelar': field_amount_total - field_amount_abonado,
                            'invoice_lines': invoice_lines
                        })
            
            if len(invoices) == 0:
                raise ValidationError(_('No se encontraron registros.'))
                lista_vendedores = list(dict.fromkeys(lista_vendedores))

            datas.append({
                'company_currency_id': self.company_currency_id.id,
                'invoices': invoices,
                'lista_vendedores': lista_vendedores
            }) 

            res = {
                'documents': datas,
                'start_date': self.from_date.strftime("%d/%m/%Y"),
                'end_date': self.to_date.strftime("%d/%m/%Y"),                
            }
            
            data = {
                'form': res
            }
            
            return self.env.ref('eu_account_reports.report_list_accounts_receivable_product').report_action(self, data=data)