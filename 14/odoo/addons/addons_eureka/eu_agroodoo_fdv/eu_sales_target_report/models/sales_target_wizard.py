# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class SalesTargetWizard(models.TransientModel):
    _name = 'sales.target.wizard'

    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')

    sales_person_id = fields.Many2one('res.users',string="Vendedor")

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('open', 'Abierto'),
        ('closed', 'Cerrado'),
    ], string='Estado', default='')

    def sales_target(self):
        datos_padre = []
        datos_hijos = []
        product_ids = []
        domain=[]
        estatus = ''

        if self.date_start:
            domain.append(('create_date','>=',self.date_start))
        if self.date_end:
            domain.append(('create_date','<=',self.date_end))
        if self.state:
            domain.append(('state','=',self.state))
        if self.state:
            if self.state == 'draft':
                estatus = 'Borrador'
            elif self.state == 'open':
                estatus = 'Abierto'
            elif self.state == 'closed':
                estatus = 'Cerrado'
            domain.append(('sales_person_id','=',self.sales_person_id.id))
        
        sales_target = self.env['saletarget.saletarget'].search(domain)
        
        for st in sales_target:
            cartera_clientes = len(self.env['res.partner'].search([('user_id', '=', st.sales_person_id.id)]))
            datos_padre.append({
                'id' : st.id,
                'name' : st.name,
                'vendedor' : st.sales_person_id.name,
                'fecha_inicio': st.start_date,
                'fecha_final': st.end_date,
                'meta': st.target_achieve,
                'meta_alcanzar': st.target,
                'meta_restante': st.difference,
                'meta_lograda': st.achieve,
                'meta_porcentaje': st.achieve_percentage,
                'cotizado': st.cotizado,
                'dias_habiles': st.dias_habiles,
                'dias_transcurridos': st.dias_transcurridos,
                'cartera_clientes': cartera_clientes,
                })

        for st_line in sales_target.target_line_ids:
            datos_hijos.append({
                'id' : st_line.reverse_id.id,
                'producto' : st_line.product_id.product_tmpl_id.name,
                'cotizado' : st_line.cotizado,
                'cantidad_meta' : st_line.target_quantity,
                'cantidad_logrado' : st_line.achieve_quantity,
                'cantidad_logrado_porc' : st_line.achieve_perc,
                })

        data = {

            'ids': self.ids,
            'model': self._name,
            'datos_padre': datos_padre,
            'datos_hijos': datos_hijos,
            'sales_person_id': self.sales_person_id.name if self.sales_person_id else '',
            'date_start': self.date_start.date() if self.date_start else '',
            'date_end': self.date_end.date() if self.date_end else '',
            'estatus': estatus if self.state else '',
        }

        return self.env.ref('eu_sales_target_report.sales_target_report').report_action(self, data=data)

