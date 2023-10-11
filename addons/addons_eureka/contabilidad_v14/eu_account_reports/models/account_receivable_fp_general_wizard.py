from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
import re

class AccountReceivableFpGeneralWizard(models.TransientModel):
    _name = "account.receivable.fp.general.wizard"

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    # invoice_user_id = fields.Many2many("res.users", string="Comercial")
    partner_ids = fields.Many2many('res.partner', string='Cliente')
    user_ids = fields.Many2many("res.users", string="Vendedor")
    product_ids = fields.Many2many("product.product", string="Producto", domain=[('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO')])
    invoice_ids = fields.Many2many("account.move", string="Factura")
    start_date = fields.Date(string='Desde')
    end_date = fields.Date(string='Hasta')    
    # Ids de productos cuya categoría es producto terminado:
    filtered_product_terminado_ids = fields.Many2many(
        'product.product',
        'product_terminado_arfpg_wizard_rel', 'wizard_id', 'product_id',
        string='Productos terminados',
        compute='_compute_filtered_product_terminado_ids',
        store=True
    )
    
    def extraer_numeros_enteros(self, cadena):
        numeros = re.findall(r'\d+', cadena)
        return int(numeros[:1].pop())

    @api.depends('company_id')
    def _compute_filtered_product_terminado_ids(self):
        for rec in self:
            domain = [
                ('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO'),
            ]
            data = rec.env['product.product'].search(domain)
            # raise UserError(data.ids)
            if data:
                rec.filtered_product_terminado_ids = data.ids

    @api.onchange('product_ids')
    def _get_product_ids(self):
        domain = []
        if self.filtered_product_terminado_ids:
            ids = [self.extraer_numeros_enteros(str(id)) for id in self.filtered_product_terminado_ids]
            domain = [('id', 'in', list(ids))]

        # raise UserError(domain)
        return {'domain': {'product_ids': domain}}

    def action_generate_report(self):
        company = self.company_id
        company_id = company.id
        company_currency_id = company.currency_id.id

        # Validación de fechas:
        if self.start_date > self.end_date:
            raise ValidationError(_('La fecha de inicio no puede ser mayor a la fecha fin.'))

        datas = []
        invoices = []

        # Cliente:
        param_partner_ids = '1 = 1'
        my_partner_ids= ','.join([str(i) for i in self.partner_ids.ids])
        if self.partner_ids:
            param_partner_ids = f'account_move.partner_id in ({my_partner_ids})'

        # Vendedor:
        param_user_ids = '1 = 1'
        my_user_ids = ','.join([str(i) for i in self.user_ids.ids])
        if self.user_ids:
            param_user_ids = f'account_move.invoice_user_id in ({my_user_ids})'

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

        # SQL a la tabla 'account.move':
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
            account_move.invoice_user_id,
            account_move.currency_id AS invoice_currency_id
            
            FROM account_move 

            LEFT JOIN account_journal ON account_journal.id = account_move.journal_id
            
            -- Cliente:
            WHERE {param_partner_ids}
            -- Vendedor:
            AND {param_user_ids}
            -- Factura:
            AND {param_invoice_ids}   
                     
            AND account_move.invoice_date >= '{self.start_date}'
            AND account_move.invoice_date <= '{self.end_date}'
            AND account_move.state = 'posted'
            AND account_move.move_type = 'out_invoice'
            AND account_journal.name NOT LIKE '%PROMO%'            
            AND account_move.company_id = {str(company_id)}
            AND account_move.amount_residual != 0

            ORDER BY account_move.invoice_date ASC
        '''
        # Ejecutando:
        self._cr.execute(sql_account_move)
        account_moves = self._cr.dictfetchall()

        if len(account_moves) == 0:
            raise ValidationError(_('No se encontraron registros.'))
        else:
            for invoice in account_moves:
                id = invoice['id']
                invoice_currency_id = invoice['invoice_currency_id']

                # Determinando los campos según la moneda:
                field_amount_total = invoice['amount_total'] # Total a Pagar
                field_amount_residual = invoice['amount_residual'] # Monto Adeudado
                #if invoice_currency_id != company_currency_id: # <---- Bolívares
                #    field_amount_total = invoice['amount_ref']
                #    field_amount_residual = invoice['amount_residual_signed_ref']

                # ================ Cliente ================ #
                # SQL para la tabla 'partner_id'
                cliente_id = invoice['partner_id']
                sql_partner_cliente = f'''
                    SELECT name, city 
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
                        invoice_user_id = invoice['invoice_user_id']                
                        # SQL para la tabla 'partner_id'
                        sql_vendedor = f'''
                            SELECT 
                            res_partner.name AS nombre_vendedor
                            FROM res_users

                            LEFT JOIN res_partner ON res_partner.id = res_users.partner_id

                            WHERE res_users.id = \''''+str(invoice_user_id)+'''\'
                        '''
                        # Ejecutando:
                        self._cr.execute(sql_vendedor)
                        res_vendedor = self._cr.dictfetchall()
                        if len(res_vendedor) > 0:
                            nombre_vendedor = res_vendedor[0]['nombre_vendedor']

                if field_amount_residual > 0:
                    invoice_lines = []
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
                    # Ejecutando:
                    self._cr.execute(sql_account_move_line)
                    invoice_line_ids = self._cr.dictfetchall()                
                    if len(invoice_line_ids) > 0:
                        for line in invoice_line_ids:
                            
                            product_id = line['product_id']
                            product_uom_id = line['product_uom_id']
                            
                            if cliente_id is not None and product_id is not None:
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
                                if product_uom_id is not None:
                                    sql_uom_uom = f'''
                                        SELECT name 
                                        FROM uom_uom
                                        WHERE id = \''''+str(product_uom_id)+'''\'
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
                                        'precio_x_fardo_usd': line['price_unit'] if invoice_currency_id == company_currency_id else line['price_unit_ref'],
                                        'sub_total_usd': line['price_subtotal'] if invoice_currency_id == company_currency_id else line['price_subtotal_ref'],
                                        'product': res_product[0]['product_name'].upper() if product_id is not None else '',
                                        # 'product': 'aaa',
                                        'product_uom_name': product_uom_name,
                                        # 'product_uom_name': 'bbb',
                                    })                              
                        
                    # Agregando Saldo Abonado y Pendiente por cancelar a la primera línea:
                    if len(invoice_lines) > 0:
                        invoices.append({
                            'invoice_date': invoice['invoice_date'].strftime("%d/%m/%Y") if invoice['invoice_date'] else '',
                            'partner_id': res_partner_cliente[0]['name'].upper() if cliente_id is not None else '',
                            'city_id': res_partner_cliente[0]['city'] if res_partner_cliente[0]['city'] else '',
                            'invoice_user_id': nombre_vendedor,
                            'name': invoice['name'],
                            'field_amount_total': field_amount_total,
                            'saldo_abonado': field_amount_total - field_amount_residual,
                            'pendiente_x_cancelar': field_amount_residual,
                            'invoice_lines': invoice_lines
                        })
            
            if len(invoices) == 0:
                raise ValidationError(_('No se encontraron registros.'))

            datas.append({
                'company_currency_id': company_currency_id,
                'invoices': invoices        
            }) 

            res = {
                'documents': datas,
                'start_date': self.start_date.strftime("%d/%m/%Y"),
                'end_date': self.end_date.strftime("%d/%m/%Y"),                
            }
            
            data = {
                'form': res
            }
            
            return self.env.ref('eu_account_reports.action_report_account_receivable_fp_general').report_action(self, data=data)