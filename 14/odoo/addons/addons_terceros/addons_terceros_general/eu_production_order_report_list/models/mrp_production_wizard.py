# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class MrpProductionWizard(models.TransientModel):
    _name = 'mrp.production.wizard'

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('planned', 'Planificado'),
        ('progress', 'En Progreso'),
        ('to_close', 'Por Cerrar'),
        ('done', 'Hecho'),
    ], string='Estado', default='')

    bom_id = fields.Many2one('mrp.bom', 'Lista de Materiales')

    def orden_production(self):
        final = []
        product_ids = []
        domain=[]
        estatus = ''

        product_line_ids = []
        lista_de_materiales = []
        product_bom_line_id = []
        product_bom_line_id_submit = []

        date_clause = ""
        query_params = []
        if self.date_start:
            date_clause += " AND sml.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND sml.date <= %s"
            query_params.append(self.date_end)
        if self.bom_id:
            date_clause += " AND mp.bom_id = %s"
            query_params.append(self.bom_id.id)

        sql_mrp_production = ("""
            SELECT mp.id AS production 
            FROM stock_move_line AS sml 
            INNER JOIN mrp_production AS mp ON mp.id=sml.production_id
            WHERE sml.production_id IS NOT NULL AND mp.state='done' {date_clause}
            GROUP BY production 
            ORDER BY production
                                """.format(date_clause=date_clause))
        self.env.cr.execute(sql_mrp_production, query_params)

        mrp_production_ids = []

        for row in self.env.cr.fetchall():
            mrp_production_ids.append(row[0])

        mrp_production = self.env['mrp.production'].search([
            ('id', 'in', mrp_production_ids)
            ])

        if not mrp_production:
            raise UserError(_('No hay datos para imprimir'))

        mrp_bom_line_1 = []
        stock_move_line_1 = []
        bom_list = []
        
        for mp in mrp_production:
            if mp.bom_id.id not in bom_list:
                bom_list.append(mp.bom_id.id)
            if mp.product_id.product_tmpl_id.id not in product_bom_line_id:
                product_bom_line_id.append(mp.product_id.product_tmpl_id.id) # GUARDA LOS ID DE LOS PRODUCTOS CON LISTA
                product_bom_line_id_submit.append({
                    'product_bom_line_name':mp.product_id.name,
                    'product_bom_id':mp.product_id.product_tmpl_id.id,
                    'production_bom_id':mp.bom_id,
                    'production_product_uom_id':mp.product_uom_id.name,
                })
        
        for p_bom_line_id in product_bom_line_id:
            mrp_bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', p_bom_line_id)
                ])
            for lista in mrp_bom:
                total = 0.0
                sub_total = 0.0
                lista_id = 0
                for mp in mrp_production:
                    if mp.product_id.product_tmpl_id.id == lista.product_tmpl_id.id and mp.state=='done':
                        total += mp.qty_produced
                    if lista.id==mp.bom_id.id and mp.state=='done':
                        sub_total += mp.qty_produced
                        lista_id=lista.id

                lista_de_materiales.append({
                    'product_id': lista.product_tmpl_id.id,
                    'product_uom_id': lista.product_uom_id.name,
                    'nombre_lista': lista.code,
                    'bom_id': lista.id,
                    'product_name': lista.product_tmpl_id.name,
                    'total_producido_por_producto': total,
                    'total_producido_por_lista': sub_total,
                    'lista_id': lista_id,
                })

        for id in bom_list:
            mrp_bom_line_1 = self.env['mrp.bom.line'].search([
                ('bom_id', '=', id)
            ])
            for mbl in mrp_bom_line_1:
                bom_id= mbl.bom_id.id
                product_tmpl_name = mbl.bom_id.product_tmpl_id.name
                product_tmpl_id = mbl.bom_id.product_tmpl_id.id
                product_line_formula = 0.0

                domain_2 = [('product_id', '=', mbl.product_id.id),
                            ('production_id', '!=', False),
                            ('move_id.picking_type_id.code', '=', 'mrp_operation'),
                            ('state', '=', 'done'),]
                if self.date_start:
                    domain_2.append(('date', '>=', self.date_start))
                if self.date_end:
                    domain_2.append(('date', '<=', self.date_end))

                stock_move_line_1 = self.env['stock.move.line'].search(domain_2)
                #raise UserError(_('IDs %s')% (stock_move_line_1))
                consumo = 0.0
                
                stock_move_0 = []
                for sml in stock_move_line_1:
                    if sml.production_id.bom_id==mbl.bom_id:
                        consumo += sml.qty_done
           
                estimado = 0.0
                total_producido_por_producto = 0.0
                for x in mrp_production:
                    if x.bom_id == mbl.bom_id:
                        total_producido_por_producto += x.qty_produced

                        stock_move_0 = self.env['stock.move'].search([
                            ('raw_material_production_id', '=', x.id),
                            ('product_id', '=', mbl.product_id.id),
                        ])
                        producto = 0
                        for est in stock_move_0.sorted(key=lambda m: (m.product_id , m.id)):
                            if producto != est.product_id:
                                estimado += est.product_uom_qty
                                #estimado = sum(est.filtered(lambda x: x.id).mapped('product_uom_qty'))
                            producto = est.product_id
                            
                merma = 0.0 
                if consumo > 0:
                    merma = consumo-estimado

                porcentaje = 0.0
                if merma > 0.0:
                    porcentaje = (merma/estimado)*100
               
                product_line_ids.append({
                    'product_line_name':mbl.product_id.name,
                    'product_line_uom_id':mbl.product_uom_id.name,
                    'product_line_formula':mbl.product_qty,
                    'bom_id': mbl.bom_id.id,
                    'product_tmpl_id': mbl.bom_id.product_tmpl_id.id,
                    'consumo': consumo,
                    'estimado':estimado,
                    'merma':merma,
                    'porcentaje':porcentaje,
                })
       

        data = {

            'ids': self.ids,
            'model': self._name,
            'move': final,
            'product_line_ids':product_line_ids,
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
            'estatus': estatus,
            'lista_de_materiales': lista_de_materiales,
            'product_bom_line_id_submit': product_bom_line_id_submit,
        }

        return self.env.ref('eu_production_order_report_list.mrp_production_report').report_action(self, data=data)

