from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProcessedPaymentsDayVendor(models.TransientModel):
    _name = "processed.payments.day.vendor"

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    invoice_user_ids = fields.Many2many("res.users", string="Comercial")
    products_ids = fields.Many2many("product.product", string="Producto", domain=[
                                    ('categ_id.complete_name', 'ilike', 'PRODUCTO TERMINADO')])
    # UPDATE
    partner_zone_ids = fields.Many2many('res.partner.zones', string='Zona')
    start_date = fields.Date(string='Desde')
    end_date = fields.Date(string='Hasta')

    def action_generate_report(self):
        company = self.company_id
        company_id = company.id
        company_currency_id = company.currency_id.id

        # Validación de fechas:
        if self.start_date > self.end_date:
            raise ValidationError(_('La fecha de inicio no puede ser mayor a la fecha fin.'))

        datas = []
        vendors_data = []
        total_vendors_quantity = 0
        total_vendors_amount = 0

        param_res_users_id = '1 = 1'
        mis_users = ','.join([str(i) for i in self.invoice_user_ids.ids])
        if self.invoice_user_ids:
            param_res_users_id = f'res_users.id in ({mis_users})'

        param_product_id = "product_category.complete_name LIKE '%PRODUCTO TERMINADO%'"
        my_products = ','.join([str(i) for i in self.products_ids.ids])
        if self.products_ids:
            param_product_id = f'account_move_line.product_id IN ({my_products})'

        # Zona:
        param_zones = ''
        mis_zones = ','.join([str(i) for i in self.partner_zone_ids.ids])
        if self.partner_zone_ids:
            param_zones = f'AND account_move.partner_zone in ({mis_zones})'

        # SQL a la tabla 'res_users':
        sql_res_users = f'''
            SELECT 
            
            res_users.id, 
            res_partner.name
            
            FROM res_users

            LEFT JOIN res_partner ON res_partner.id = res_users.partner_id

            WHERE {param_res_users_id}
            AND res_users.company_id = {str(company_id)}
        '''
        # Ejecutando:
        self._cr.execute(sql_res_users)
        res_res_users = self._cr.dictfetchall()
        currency_ids = []

        if len(res_res_users) > 0:
            for res_users in res_res_users:
                # Datos del usuario:
                invoice_user_id = res_users['id']
                user_name = res_users['name']

                sold_products_vendor = []
                invoice_lines = []

                # Verificando si el usuario es un empleado de la compañía actual:
                res_users_code = ''
                # SQL a la tabla 'hr_employee':
                sql_hr_employee = f'''
                    SELECT name, emp_id 
                    FROM hr_employee
                    WHERE user_id = {str(invoice_user_id)}
                '''
                # Ejecutando:
                self._cr.execute(sql_hr_employee)
                res_hr_employee = self._cr.dictfetchall()
                if len(res_hr_employee) > 0:
                    res_users_code = res_hr_employee[0]['emp_id']
                    # user_name = res_hr_employee[0]['name']
                # =========================================================== #
                # SQL a la tabla 'account_move':
                sql_account_move = f'''
                    SELECT 
                    
                    account_move.currency_id AS invoice_currency_id,
                    account_move.id, 
                    account_move.partner_id, 
                    account_move.invoice_date, 
                    account_move.name, 
                    account_move.amount_total,
                    account_move.amount_residual, 
                    account_move.invoice_user_id, 
                    account_move.move_type,
                    account_journal.name AS journal_name
                    
                    FROM account_move 

                    LEFT JOIN account_journal ON account_journal.id = account_move.journal_id

                    WHERE account_move.invoice_user_id = {invoice_user_id}
                    -- Zona:
                    {param_zones}                               
                    AND account_move.invoice_date >= '{self.start_date}'
                    AND account_move.invoice_date <= '{self.end_date}'
                    AND account_move.state = 'posted'
                    AND account_move.move_type = 'out_invoice'
                    AND account_journal.name NOT LIKE '%PROMO%'
                    AND account_move.company_id = {str(company_id)}
                '''
                # Ejecutando:
                self._cr.execute(sql_account_move)
                account_moves = self._cr.dictfetchall()

                if len(account_moves) > 0:
                    for invoice in account_moves:
                        id = invoice['id']
                        invoice_currency_id = invoice['invoice_currency_id']

                        # SQL a la tabla 'account.move.line':
                        sql_account_move_line = f'''
                            SELECT 
                            
                            account_move_line.id, 
                            account_move_line.product_id, 
                            account_move_line.quantity, 
                            account_move_line.price_unit, 
                            account_move_line.price_subtotal,
                            account_move_line.price_subtotal_ref,
                            account_move_line.product_uom_id
                            
                            FROM account_move_line
                            
                            LEFT JOIN product_product ON product_product.id = account_move_line.product_id
                            LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                            LEFT JOIN product_category ON product_category.id = product_template.categ_id

                            WHERE account_move_line.move_id = {str(id)}
                            AND {param_product_id}
                        '''
                        # Ejecutando:
                        self._cr.execute(sql_account_move_line)
                        invoice_line_ids = self._cr.dictfetchall()
                        if len(invoice_line_ids) > 0:
                            for line in invoice_line_ids:
                                product_id = line['product_id']
                                product_id = line['product_id']
                                product_uom_id = line['product_uom_id']

                                if product_id is not None:
                                    # ================ Producto ================ #
                                    # SQL para la tabla 'product.product'
                                    sql_product_product = f'''
                                        SELECT 

                                        product_product.id,
                                        product_product.product_tmpl_id,
                                        product_category.complete_name,  
                                        product_template.name AS product_name,
                                        product_product.default_code

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

                                    if product_id is not None and len(res_product) > 0:
                                        invoice_lines.append({
                                            'product_id': product_id,
                                            'default_code': res_product[0]['default_code'] if product_id is not None else '',
                                            'product_name': res_product[0]['product_name'].upper() if product_id is not None else '',
                                            # 'product_name': res_product[0]['product_name']['es_VE'].upper() if product_id is not None else '',
                                            'product_uom_name': product_uom_name,
                                            'quantity': line['quantity'],
                                            'price_subtotal': line['price_subtotal'] if invoice_currency_id == company_currency_id else line['price_subtotal_ref'],
                                            # 'price_subtotal': line['price_subtotal'],
                                        })

                if len(invoice_lines) > 0:
                    product_ids = [dic['product_id'] for dic in invoice_lines]
                    product_ids = list(dict.fromkeys(product_ids))

                    for product_id_loop in product_ids:
                        list_product_data = [
                            elem for elem in invoice_lines if elem['product_id'] == product_id_loop]

                        total_quantity = 0
                        total_amount = 0
                        for product_data in list_product_data:
                            total_quantity += product_data['quantity']
                            total_amount += product_data['price_subtotal']

                        sold_products_vendor.append({
                            'product_name': list_product_data[0]['product_name'],
                            'total_quantity': total_quantity,
                            'product_uom_name': list_product_data[0]['product_uom_name'],
                            'total_amount': total_amount,
                        })

                        # Total de cantidades y montos (En General):
                        total_vendors_quantity += total_quantity
                        total_vendors_amount += total_amount

                if len(sold_products_vendor) > 0:
                    sold_products_vendor = sorted(
                        sold_products_vendor, key=lambda d: d['total_quantity'], reverse=True)
                    vendors_data.append({
                        'user_name': user_name,
                        'res_users_code': res_users_code,
                        'sold_products_vendor': sold_products_vendor
                    })

            if len(vendors_data) == 0:
                raise ValidationError(
                    _('No se encontraron registros de empleados con ventas realizadas.'))

            # Calculando porcentaje por línea de producto de cada vendedor:
            # total_vendors_percentage = 0
            for dict_vendor_data in vendors_data:
                sold_products_vendor = dict_vendor_data['sold_products_vendor']
                for i in range(len(sold_products_vendor)):
                    row = sold_products_vendor[i]
                    total_amount = row['total_amount']
                    percentage = (total_amount * 100) / total_vendors_amount
                    # percentage = float("{:.5f}".format(percentage))
                    # if percentage > 0:
                    #     percentage = float(f'{percentage:.5f}')
                    percentage = "{:.4f}".format(round(percentage, 4))

                    row['percentage'] = percentage
                    # total_vendors_percentage += percentage

            def format_percentage(self, percentage):
                percentage = "{:.4f}".format(round(percentage, 4))
                return percentage

            datas.append({
                'company_currency_id': company_currency_id,
                'vendors_data': vendors_data,
                'total_vendors_quantity': total_vendors_quantity,
                'total_vendors_amount': total_vendors_amount,
                'format_percentage': format_percentage
                # 'total_vendors_percentage': total_vendors_percentage
            })

            res = {
                'documents': datas,
                'start_date': self.start_date.strftime("%d/%m/%Y"),
                'end_date': self.end_date.strftime("%d/%m/%Y"),
            }

            data = {
                'form': res
            }

            return self.env.ref('eu_sales_kpi_kg.action_report_processed_payments_day_vendor').report_action(self, data=data)
        else:
            raise ValidationError(
                _('No se encontraron registros según los datos ingresados.'))
