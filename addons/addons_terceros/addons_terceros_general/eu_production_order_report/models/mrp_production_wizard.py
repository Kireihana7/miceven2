# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProductionReportWizard(models.TransientModel):
    _name = 'mrp.production.report.wizard'

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')

    def print_report(self):

        datos = []
        producciones = []
        ordenes_de_trabajo = []
        componentes = []
        sub_productos = []

        domain = [('state','=','done')]

        if self.date_start:
            domain.append(('date_finished', '>=', self.date_start))
        if self.date_end:
            domain.append(('date_finished', '<=', self.date_end))

        mrp_production = self.env['mrp.production'].search(domain)

        for mp in mrp_production:

            producciones.append({
                'id': mp.id,
                'name': mp.name,
                'user_id': mp.user_id.name,
                'product_id': mp.product_id.name,
                'product_qty': mp.product_qty,
                'qty_producing': mp.qty_producing,
                'bom_id': mp.bom_id.code,
                'date_planned_start':mp.date_planned_start,
                'date_finished':mp.date_finished,
                'state':mp.state,
                })

            if len(mp.move_raw_ids) > 0: #COMPONENTES
                for mri in mp.move_raw_ids:
                    formula_computada = mp.product_uom_id._compute_quantity(mp.product_qty, mp.product_id.uom_id)
                    cantidad_material = mp.bom_id.product_uom_id._compute_quantity(mp.bom_id.product_qty, mp.bom_id.product_tmpl_id.uom_id)
                    formula = ((mri.bom_line_id.product_qty / cantidad_material) * (formula_computada))
                    componentes.append({
                        'product_id':mri.product_id.name,
                        'product_uom_qty':mri.product_uom_qty,
                        'quantity_done':mri.quantity_done,
                        'product_uom':mri.product_uom.name,
                        'raw_material_production_id':mri.raw_material_production_id.id,
                        'formula_computada': formula_computada,
                        'cantidad_material': cantidad_material,
                        'formula': formula,
                        })

            if len(mp.workorder_ids) > 0: #ORDENES DE TRABAJO
                for wi in mp.workorder_ids:
                    ordenes_de_trabajo.append({
                        'name': wi.name,
                        'workcenter_id': wi.workcenter_id.name,
                        'date_planned_start': wi.date_planned_start,
                        'duration_expected': wi.duration_expected,
                        'duration': wi.duration,
                        'state':wi.state,
                        'production_id':wi.production_id.id,
                        })

            if len(mp.move_byproduct_ids) > 0: #SUBPRODUCTOS
                for mbi in mp.move_byproduct_ids:
                    sub_productos.append({
                        'product_id':mbi.product_id.name,
                        'product_uom_qty':mbi.product_uom_qty,
                        'quantity_done':mbi.quantity_done,
                        'product_uom':mbi.product_uom.name,
                        'production_id':mbi.production_id.id if mbi.production_id.id else False,
                        })

                #raise UserError(sub_productos)

        data = {

            'producciones': producciones,
            'componentes': componentes,
            'ordenes_de_trabajo': ordenes_de_trabajo,
            'sub_productos': sub_productos,
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
        }



        return self.env.ref('eu_production_order_report.mrp_production_report').report_action(self, data=data)