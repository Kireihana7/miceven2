from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountReceivableFpGeneralWizard(models.TransientModel):
    _name = "clientes.prepago.wizard"

    company_id = fields.Many2one('res.company', string='Compañía')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    start_date = fields.Datetime(string='Desde')
    end_date = fields.Datetime(string='Hasta')    

    def action_generate_report(self):
        company = self.company_id
        company_id = company.id
        company_currency_id = company.currency_id.id

        datas = []
        sales = []
        
        param_partner_id = '1 = 1'
        if self.partner_id:
            param_partner_id = f'partner_id = {self.partner_id.id}'

        # SQL a la tabla 'sale_order':
        sql_sale_order = f'''
            SELECT 
            
            id,
            currency_id,
            name,
            date_order

            FROM sale_order 
            
            WHERE {param_partner_id}
            AND date_order >= '{self.start_date}'
            AND date_order <= '{self.end_date}'
            AND state = 'sale'
            AND company_id = {str(company_id)}
        '''
        # Ejecutando:
        self._cr.execute(sql_sale_order)
        sale_orders = self._cr.dictfetchall()

        # Inicializando variables:
        total_cargas_negociadas = 0
        total_cargas_despachadas = 0
        total_cargas_x_despachar = 0

        total_cantidad_fardos = 0
        total_cantidad_x_kg = 0

        total_qty_x_kg_cargas_negociadas = 0
        total_qty_x_kg_cargas_despachadas = 0

        if len(sale_orders) == 0:
            raise ValidationError(_('No se encontraron ventas según los datos ingresados.'))
        else:
            for sale_order in sale_orders:
                sale_currency_id = sale_order['currency_id']
                sale_id = sale_order['id']

                sale_order_lines = []
                stock_move_lines = []

                # ====================== 'sale_order_line' ====================== #
                # SQL a la tabla 'sale_order_line':
                sql_sale_order_line = f'''
                    SELECT 

                    sale_order_line.product_uom, 
                    sale_order_line.product_uom_qty, 
                    sale_order_line.qty_delivered, 
                    sale_order_line.price_unit,
                    sale_order_line.price_unit_ref,
                    product_template.name AS product_name
                    
                    FROM sale_order_line

                    LEFT JOIN product_product ON product_product.id = sale_order_line.product_id
                    LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                    LEFT JOIN product_category ON product_category.id = product_template.categ_id

                    WHERE sale_order_line.order_id = \''''+str(sale_id)+'''\'
                '''
                # Ejecutando:
                self._cr.execute(sql_sale_order_line)
                res_sale_order_lines = self._cr.dictfetchall()

                # Datos totales de la SO:
                qty_x_fardos_negociadas_so = 0
                qty_x_kg_negociadas_so = 0

                qty_x_fardos_despachadas_so = 0
                qty_x_kg_despachadas_so = 0                
                
                total_qty_despachar_x_fardos_so = 0
                total_qty_despachar_x_kg_so = 0

                if len(res_sale_order_lines) > 0:
                    for sale_line in res_sale_order_lines:
                        product_uom = sale_line['product_uom']
                        cantidad_negociada = sale_line['product_uom_qty']
                        cantidad_despachada = sale_line['qty_delivered']

                        total_cargas_negociadas += cantidad_negociada
                        total_cargas_despachadas += cantidad_despachada

                        # Calculando cantidades por kg:
                        # ================ Unidad de Medida ================ #
                        # SQL para la tabla 'uom_uom'
                        qty_x_kg_cargas_negociadas = 0
                        qty_x_kg_cargas_despachadas = 0
                        if product_uom is not None:
                            sql_uom_uom_po_line = f'''
                                SELECT id, name
                                FROM uom_uom
                                WHERE id = \''''+str(product_uom)+'''\'
                            '''
                            # Ejecutando:
                            self._cr.execute(sql_uom_uom_po_line)
                            res_uom_uom_po_line = self._cr.dictfetchall()
                            if len(res_uom_uom_po_line) > 0:
                                uom_id = res_uom_uom_po_line[0]['id']

                                factor_inv = self.env['uom.uom'].search([('id', '=', str(uom_id))]).factor_inv
                                if factor_inv:
                                    qty_x_kg_cargas_negociadas = cantidad_negociada * factor_inv
                                    qty_x_kg_cargas_despachadas = cantidad_despachada * factor_inv

                                    # ========== SO ========== #
                                    # Negociadas:
                                    qty_x_fardos_negociadas_so += cantidad_negociada # Fardos
                                    qty_x_kg_negociadas_so += qty_x_kg_cargas_negociadas # Kg

                                    # Despachadas:
                                    qty_x_fardos_despachadas_so += cantidad_despachada # Fardos
                                    qty_x_kg_despachadas_so += qty_x_kg_cargas_despachadas # Kg                                    

                        total_qty_x_kg_cargas_negociadas += qty_x_kg_cargas_negociadas
                        total_qty_x_kg_cargas_despachadas += qty_x_kg_cargas_despachadas      

                        # Líneas de la venta:
                        cantidad_x_despachar = sale_line['product_uom_qty'] - sale_line['qty_delivered']
                        if cantidad_x_despachar < 0:
                            cantidad_x_despachar = 0
                        
                        price_unit = sale_line['price_unit'] if sale_currency_id == company_currency_id else sale_line['price_unit_ref']
                        sale_order_lines.append({
                            'product_name': sale_line['product_name'],
                            'product_uom_qty': sale_line['product_uom_qty'],
                            'price_unit': price_unit,
                            'qty_delivered': sale_line['qty_delivered'],
                            'monto_negociado': price_unit * sale_line['product_uom_qty'],
                            'monto_despachado': price_unit * sale_line['qty_delivered'],
                            'cantidad_x_despachar': cantidad_x_despachar,
                        })

                    # Totales de las líneas de la SO:      
                    total_qty_despachar_x_fardos_so = qty_x_fardos_negociadas_so - qty_x_fardos_despachadas_so
                    total_qty_despachar_x_kg_so = qty_x_kg_negociadas_so - qty_x_kg_despachadas_so
                                                                                         

                # ====================== 'stock_picking' ====================== #
                # SQL a la tabla 'stock_picking':
                # LEFT JOIN stock_picking_type ON stock_picking_type.id = stock_picking.picking_type_id
                sql_stock_picking = f'''
                    SELECT *
                    FROM stock_picking
                    WHERE sale_id = \''''+str(sale_id)+'''\'
                '''
                # Ejecutando:
                self._cr.execute(sql_stock_picking)
                stock_pickings = self._cr.dictfetchall()

                if len(stock_pickings) > 0:
                    for picking in stock_pickings:
                        picking_id = picking['id']
                        # SQL a la tabla 'stock_move_line':

                        # stock_move_line = f'''
                        #     SELECT 
                            
                        #     stock_move_line.product_id,
                        #     stock_move_line.product_uom_id,
                        #     stock_move_line.qty_done,
                        #     stock_move_line.id
                            
                        #     FROM stock_move_line
                            
                        #     LEFT JOIN product_product ON product_product.id = stock_move_line.product_id
                        #     LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
                        #     LEFT JOIN product_category ON product_category.id = product_template.categ_id

                        #     WHERE stock_move_line.picking_id = \''''+str(picking_id)+'''\'
                        # '''

                        stock_move_line = f'''
                            SELECT 
                            
                            product_id,
                            product_uom_id,
                            qty_done,
                            id
                            
                            FROM stock_move_line

                            WHERE picking_id = \''''+str(picking_id)+'''\'
                        '''

                        # Ejecutando:
                        self._cr.execute(stock_move_line)
                        res_stock_move_line = self._cr.dictfetchall()                
                        if len(res_stock_move_line) > 0:
                            for line in res_stock_move_line:
                                cliente_id = picking['partner_id']
                                product_id = line['product_id']
                                product_uom_id = line['product_uom_id']
                                driver_id = picking['driver_id']
                                vehicle_id = picking['vehicle_id']

                                if cliente_id is not None and product_id is not None:
                                    # ================ Cliente ================ #
                                    # SQL para la tabla 'partner_id'
                                    sql_partner_cliente = f'''
                                        SELECT name 
                                        FROM res_partner
                                        WHERE id = \''''+str(cliente_id)+'''\'
                                    '''
                                    # Ejecutando:
                                    self._cr.execute(sql_partner_cliente)
                                    res_partner_cliente = self._cr.dictfetchall()

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
                                    factor_inv = ''
                                    cantidad_x_fardo = line['qty_done']
                                    cantidad_x_kg = 0
                                    if product_uom_id is not None:
                                        sql_uom_uom = f'''
                                            SELECT id, name
                                            FROM uom_uom
                                            WHERE id = \''''+str(product_uom_id)+'''\'
                                        '''
                                        # Ejecutando:
                                        self._cr.execute(sql_uom_uom)
                                        res_uom_uom = self._cr.dictfetchall()
                                        if len(res_uom_uom) > 0:
                                            uom_id = res_uom_uom[0]['id']
                                            product_uom_name = res_uom_uom[0]['name']

                                            factor_inv = self.env['uom.uom'].search([('id', '=', str(uom_id))]).factor_inv
                                            if factor_inv:
                                                cantidad_x_kg = cantidad_x_fardo * factor_inv

                                    # ================ Conductor ================ #
                                    res_partner_driver = []
                                    if driver_id is not None:
                                        # SQL para la tabla 'partner_id'
                                        sql_partner_driver = f'''
                                            SELECT name
                                            FROM res_partner
                                            WHERE id = \''''+str(driver_id)+'''\'
                                        '''
                                        # Ejecutando:
                                        self._cr.execute(sql_partner_driver)
                                        res_partner_driver = self._cr.dictfetchall()                                        

                                    # ================ Vehículo ================ #
                                    res_vehicle = []
                                    if vehicle_id is not None:                                    
                                        # SQL para la tabla 'fleet_vehicle'
                                        sql_vehicle = f'''
                                            SELECT 
                                            name,
                                            license_plate 
                                            FROM fleet_vehicle
                                            WHERE id = \''''+str(vehicle_id)+'''\'
                                        '''
                                        # Ejecutando:
                                        self._cr.execute(sql_vehicle)
                                        res_vehicle = self._cr.dictfetchall()

                                    if product_id is not None and res_product[0]['product_tmpl_id'] is not None:
                                        stock_move_lines.append({
                                            'id': line['id'],
                                            'so': sale_order['name'],
                                            'date_done': picking['date_done'].strftime("%d/%m/%Y") if picking['date_done'] else '',
                                            'partner_id': res_partner_cliente[0]['name'].upper() if len(res_partner_cliente) > 0 else '',
                                            'name': picking['name'],
                                            'cantidad_x_fardo': cantidad_x_fardo,
                                            'cantidad_x_kg': cantidad_x_kg,
                                            'product': res_product[0]['product_name'].upper() if product_id is not None else '',
                                            # 'product': 'aaa',
                                            'product_uom_name': product_uom_name,
                                            'driver_id': res_partner_driver[0]['name'].upper() if len(res_partner_driver) > 0 else '',
                                            'vehicle_id': res_vehicle[0]['name'].upper() if len(res_vehicle) > 0 else '',
                                            'vehicle_license_plate': res_vehicle[0]['license_plate'].upper() if len(res_vehicle) > 0 and res_vehicle[0]['license_plate'] is not None else '',
                                        })                              


                                    total_cantidad_fardos += cantidad_x_fardo
                                    total_cantidad_x_kg += cantidad_x_kg

                if len(sale_order_lines) > 0 and len(stock_move_lines) > 0:
                    sales.append({
                        'name': sale_order['name'],
                        'date_order': sale_order['date_order'].strftime("%d/%m/%Y") if sale_order['date_order'] is not None else '',
                        # ==================== SO ==================== #
                        'sale_order_lines': sale_order_lines,
                        # Datos totales de la SO:
                        'qty_x_fardos_negociadas_so': qty_x_fardos_negociadas_so,
                        'qty_x_kg_negociadas_so': qty_x_kg_negociadas_so,

                        'qty_x_fardos_despachadas_so': qty_x_fardos_despachadas_so,
                        'qty_x_kg_despachadas_so': qty_x_kg_despachadas_so,                
                        
                        'total_qty_despachar_x_fardos_so': total_qty_despachar_x_fardos_so,
                        'total_qty_despachar_x_kg_so': total_qty_despachar_x_kg_so,

                        # ==================== Movimientos ==================== #
                        'stock_move_lines': stock_move_lines
                    })

        # Total cargas por despachar:
        total_cargas_x_despachar = total_cargas_negociadas - total_cargas_despachadas
        # Total cantidad de cargas por kilos:
        total_qty_x_kg_negociadas_despachadas = total_qty_x_kg_cargas_negociadas - total_qty_x_kg_cargas_despachadas

        if len(sales) == 0:
            raise ValidationError(_('No se encontraron ventas con movimientos de inventario.'))
        
        # Enviando datos:
        datas.append({
            'company_currency_id': company_currency_id,
            'sales': sales,
            'total_cantidad_fardos': total_cantidad_fardos,
            'total_cantidad_x_kg': total_cantidad_x_kg,

            'total_cargas_negociadas': total_cargas_negociadas,
            'total_cargas_despachadas': total_cargas_despachadas,
            'total_cargas_x_despachar': total_cargas_x_despachar,

            'total_qty_x_kg_cargas_negociadas': total_qty_x_kg_cargas_negociadas,
            'total_qty_x_kg_cargas_despachadas': total_qty_x_kg_cargas_despachadas,
            'total_qty_x_kg_negociadas_despachadas': total_qty_x_kg_negociadas_despachadas,                              
        }) 

        res = {
            'documents': datas,
            'start_date': self.start_date.strftime("%d/%m/%Y"),
            'end_date': self.end_date.strftime("%d/%m/%Y"),                
        }
        
        data = {
            'form': res
        }
        
        return self.env.ref('eu_reporte_clientes_prepago.action_report_clientes_prepago').report_action(self, data=data)    