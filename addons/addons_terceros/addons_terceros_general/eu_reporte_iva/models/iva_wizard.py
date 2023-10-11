# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class IvaWizard(models.TransientModel):
    _name = 'iva.wizard'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente')
    state = fields.Selection([
        ('confirmed', 'Confirmado'),
        ('withhold', 'Retenido'),
        ('declared', 'Declarado'),
        ('done', 'Hecho'),
    ], string='Estatus de la retención')

    type_invoice = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
    ], string='Retenciones de IVA', default='in_invoice', required=True,)

    def report_iva(self):
        final = []
        date_clause = ""
        query_params = []
        type_invoice_view = ''
        estatus_view = ''
        if self.date_start:
            date_clause += " AND awi.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND awi.date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND awi.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.state:
            date_clause += " AND awi.state = %s"
            query_params.append(self.state)
            if self.state == 'confirmed':
                estatus_view = 'Confirmado'
            elif self.state == 'withhold':
                estatus_view = 'Retenido'
            elif self.state == 'declared':
                estatus_view = 'Declarado'
            elif self.state == 'done':
                estatus_view = 'Hecho'

        if self.type_invoice:
            date_clause += " AND awi.move_type = %s"
            query_params.append(self.type_invoice)
            if self.type_invoice == 'in_invoice':
                type_invoice_view = 'Cuentas Por Pagar'
            else:
                type_invoice_view = 'Cuentas Por Cobrar'

        sql_iva = ("""        

            SELECT awi.number as comprobante, awi.date as fecha, am.name as factura, 
            (SELECT rif||'/'||name FROM res_partner WHERE id=awi.partner_id) as proveedor,
            am.amount_total as monto_total, SUM(awil.base_tax) as base_imponible, act.amount as iva, 
            SUM(awil.amount_tax) as impuesto, 
            awil.rate_amount as porcentaje, am.amount_wh_iva as monto, awi.state as estatus FROM
            account_tax as act 
            inner join account_wh_iva_line as awil on awil.ret_tax=act.id
            inner join account_wh_iva as awi on awi.id=awil.retention_id
            inner join account_move as am on am.wh_id=awi.id 
            WHERE awi.state!='annulled' and awi.state!='cancel' and awi.state!='draft' {date_clause}
            GROUP BY comprobante, fecha, factura, proveedor, iva, porcentaje, awi.state, monto, monto_total
            ORDER BY comprobante

                                """.format(date_clause=date_clause))
        self.env.cr.execute(sql_iva, query_params)
        query_result = self.env.cr.dictfetchall()
            
        if len(query_result)>0:
            for row in query_result:

                proveedor_rif = row['proveedor'].split('/')
                final.append({
                    'comprobante': row['comprobante'],
                    'fecha': row['fecha'],
                    'proveedor': proveedor_rif[1],
                    'rif': proveedor_rif[0],
                    'monto_total': row['monto_total'],
                    'base_imponible': row['base_imponible'],
                    'iva': row['iva'],
                    'impuesto': row['impuesto'],
                    'porcentaje': row['porcentaje'],
                    'monto': row['monto'],
                    'estatus': row['estatus'],
                })
        else:
            raise UserError(_("No hay datos para imprimir"))

        data = {
            'ids': self.ids,
            'model': self._name,
            'state': estatus_view if self.state else '',
            'type_invoice': type_invoice_view if self.type_invoice else '',
            'final': final,
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'partner_id': self.partner_id.rif+' '+self.partner_id.name if self.partner_id else '',
        }

        return self.env.ref('eu_reporte_iva.iva_report').report_action(self, data=data)

