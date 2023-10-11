
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

class QualityCheckWizard(models.TransientModel):
    _name = "quality.check.wizard"

    def _get_product_operation(self):
        product_operation = self.env['quality.check'].search([('id', '=', self.env.context.get('active_id'))]).product_operation
        return product_operation

    # cantidad_imprimir = fields.Char("Rondas a Imprimir")
    # cantidad_imprimir = fields.Selection(selection=lambda self: self.dynamic_rounds(), string="Rondas a Imprimir") 
    product_operation = fields.Many2one('product.template.operation', string="Operaciones del Producto", default=_get_product_operation)
    cantidad_imprimir = fields.Many2many(
        'product.template.propiedades',
        string='Rondas a imprimir',
    )

    def dynamic_rounds(self):
        # select = [('yes', 'Yes'), ('no', 'No')]
        # return select

        quality_table = self.env['quality.check'].browse(self.env.context.get('active_id')).mapped('quality_tabla').filtered(lambda x: x.display_type == 'line_section').mapped('name')
        select = []
        for table in quality_table:
            select.append((table, table))
        return select        

    def print_quality_check_tabla(self):
        datas = []
        quality_check = self.env['quality.check'].sudo().browse(self.env.context.get('active_id'))
        
        # Todas las Rondas:
        rondas_todas = []
        quality_check_rondas = self.env['quality.check'].search([('id', '=', self.env.context.get('active_id'))]).quality_tabla
        for i in quality_check_rondas:
            diferencia = i.diferencia
            if diferencia != 0:
                diferencia = round(diferencia, 2)
            rondas_todas.append({
                'name': i.name,
                'display_type': i.display_type,
                'resultado_esperado': i.resultado_esperado,
                'resultado': i.resultado,
                'qty_expected': i.qty_expected,
                'qty': i.qty,
                'diferencia': diferencia
            })     
                    
        rondas = []
        if len(self.cantidad_imprimir) == 0:
            rondas = rondas_todas
        else:
            # Cantidad de propiedades:
            property_count = self.env['quality.check.tabla'].search_count([('quality_check', '=', self.env.context.get('active_id'))])            
            # Recorriendo las rondas
            for ronda in self.cantidad_imprimir:
                # Ronda:
                data = self.env['quality.check.tabla'].search([
                    ('propiedades', '=', ronda.id), 
                    ('quality_check', '=', self.env.context.get('active_id'))
                ])
                # Agregando ronda a la lista:
                for i in data:
                    diferencia = i.diferencia
                    if diferencia != 0:
                        diferencia = round(diferencia, 2)                    
                    rondas.append({
                        'name': i.name,
                        'display_type': i.display_type,
                        'resultado_esperado': i.resultado_esperado,
                        'resultado': i.resultado,
                        'qty_expected': i.qty_expected,
                        'qty': i.qty,
                        'diferencia': diferencia
                    })
                # Recorriendo while hasta que encuentre el siguiente line section de la ronda actual:
                i = 1
                while True:             
                    round_id = ronda.id + i      
                    # Next Record Data:
                    next_record = self.env['quality.check.tabla'].search([
                        ('propiedades', '=', round_id), 
                        ('quality_check', '=', self.env.context.get('active_id'))
                    ])
                    if len(next_record) > 0:
                        if next_record.display_type != 'line_section':                       
                            for j in next_record:
                                if diferencia != 0:
                                    diferencia = round(diferencia, 2)                                   
                                rondas.append({
                                    'name': j.name,
                                    'display_type': j.display_type,
                                    'resultado_esperado': j.resultado_esperado,
                                    'resultado': j.resultado,
                                    'qty_expected': j.qty_expected,
                                    'qty': j.qty,
                                    'diferencia': diferencia
                                })                            
                            i += 1
                        else:
                            break  
                    else:
                        if i > property_count:
                            break
                        else:
                            i += 1
                            continue             
                                                
        # Promedio de Propiedades:
        promedio_propiedades = []
        if len(rondas) > 0:
            data = rondas
            # data = rondas_todas
            names = []
            for count, ele in enumerate(data):
                my_dict = data[count]
                if my_dict['display_type'] != 'line_section':
                    names.append(my_dict['name'])
                    
            names = list(dict.fromkeys(names))
            
            for name in names:
                suma = 0
                cantidad_elementos = 0
                for count, ele in enumerate(data):
                    my_dict = data[count]
                    if my_dict['name'] == name:
                        # Tomando en cuenta solamente aquellos valores mayores a 0:
                        if float(my_dict['qty']) > 0:
                            suma += float(my_dict['qty'])
                            cantidad_elementos += 1
                
                promedio = 0
                if suma > 0:
                    promedio = suma / cantidad_elementos
                    promedio = round(promedio, 2)
                    promedio_propiedades.append({
                        'name': name,
                        'promedio': promedio
                    })                              
                # promedio_propiedades.append({
                #     'name': name,
                #     'promedio': promedio
                # })            

        # No Conformidades:
        quality_motivo = []
        if len(quality_check.quality_motivo) > 0:
            for line in quality_check.quality_motivo:
                destino = ''
                if line.destino:
                    destino = line.destino
                quality_motivo.append({
                    'name': line.name.name,
                    'quantity': line.quantity,
                    'destino': destino
                })     

        for rec in quality_check:
            datas.append({
                'name': rec.name,
                'create_date': rec.create_date - timedelta(hours=4),
                'partner_id': rec.partner_id.name,
                'vehicle_id': rec.vehicle_id.name,
                'title': rec.title,
                'product_operation': rec.product_operation.name,
                'picking_id': rec.picking_id.name,
                'product_id': rec.product_id.name,
                'lot_id': rec.lot_id.name,
                'measure': rec.measure,
                'point_id': rec.point_id.name,
                'test_type_id': rec.test_type_id.name,
                'team_id': rec.team_id.name,
                'company_id': rec.company_id.name,
                'note': rec.note,
                'additional_note': rec.additional_note,
                'rondas': rondas,
                'promedio_propiedades': promedio_propiedades,
                'quality_motivo': quality_motivo
            }) 

        res = {
            'documents': datas,
        }
        
        data = {
            'form': res
        }
        
        return self.env.ref('eu_quality_check_report.action_report_quality_check').report_action(self, data=data)