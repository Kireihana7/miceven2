# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class MrpProductionWizard(models.TransientModel):
    _name = 'islr.wizard'

    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    partner_id = fields.Many2one('res.partner', string='Proveedor o Cliente')
    move_type = fields.Selection([
        ('in_invoice', 'Cuentas Por Pagar'),
        ('out_invoice', 'Cuentas Por Cobrar'),
        ('in_refund', 'Notas de Credito'),
    ], string='Retenciones de ISLR', default='in_invoice', required=True,)

    state = fields.Selection([
        ('confirmed', 'Confirmado'),
        ('declared', 'Declarado'),
        ('done', 'Pagado'),
    ], string='Estatus de la retención')

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string="Compañia",
        readonly=True,
    )
    in_bs=fields.Boolean(string='En Bolivares')
    def report_islr(self):
        final = []
        date_clause = ""
        query_params = []
        estatus_view = ''
        if self.company_id:
            date_clause += " AND awi.company_id = %s"
            query_params.append(self.company_id.id)
        if self.date_start:
            date_clause += " AND awi.date >= %s"
            query_params.append(self.date_start)
        if self.date_end:
            date_clause += " AND awi.date <= %s"
            query_params.append(self.date_end)
        if self.partner_id:
            date_clause += " AND awi.partner_id = %s"
            query_params.append(self.partner_id.id)
        if self.move_type:
            date_clause += " AND awi.move_type = %s"
            query_params.append(self.move_type)
        if self.state:
            date_clause += " AND awi.state = %s"
            query_params.append(self.state)
            if self.state == 'confirmed':
                estatus_view = 'Confirmado'
            elif self.state == 'declared':
                estatus_view = 'Declarado'
            elif self.state == 'done':
                estatus_view = 'Pagado'

        sql_islr = ("""
            SELECT 
            awi.id, awi.date as fecha, 
            awi.number as comprobante, 
            awi.company_id, 
            awi.partner_id, 
            awi.move_type, 
            awil.descripcion||'-'||awil.code_withholding_islr as cod,
            awil.invoice_id, 
            am.amount_total as monto_total, 
            awil.base_tax as monto_base, 
            awil.ret_amount as retenido, 
            awil.porc_islr as porcentaje_islr, 
            awil.sustraendo as sustraendo, 
            rp.name as proveedor, 
            rp.residence_type as tipo_residencia, 
            rp.rif as rif, 
            rc.name, 
            awrtl.apply_up_to, 
            awrt.factor, 
            awrt.parcentage_subtracting_1 as sus_1, 
            awrt.parcentage_subtracting_3 as sus_3, 
            am.manual_currency_exchange_rate as tasa,
            am.currency_id as moneda
            FROM account_wh_islr awi
            inner join account_wh_islr_line as awil on awil.withholding_id=awi.id
            inner join res_partner as rp on rp.id=awi.partner_id
            inner join res_company as rc on rc.id=awi.company_id
            inner join account_move as am on am.id=awi.invoice_rel
            left join account_withholding_rate_table_line as awrtl on awrtl.id=awil.table_id
            left join account_withholding_rate_table as awrt on awrt.id=awrtl.table_id
            WHERE awil.withholding_id is not null {date_clause}
                                """.format(date_clause=date_clause))
        self.env.cr.execute(sql_islr, query_params)
        query_result = self.env.cr.dictfetchall()
        
        concepto = []
            
        if query_result:
            if self.in_bs:
                for row in query_result:
                    monto_cheque = 0.00
                    monto_sustraendo = 0.00
                    retenido = row['retenido'] * row['tasa']
                    
                    if row['sustraendo'] == True:
                        if row['porcentaje_islr'] == 1:
                            monto_sustraendo = row['sus_1']
                        if row['porcentaje_islr'] == 3:
                            monto_sustraendo = row['sus_3']
                        #retenido = retenido - monto_sustraendo

                    if row['cod'] not in concepto:
                        concepto.append(row['cod'])
                    
                    if row['moneda'] == self.env.company.currency_id.id:
                        monto_total= row['monto_total'] * row['tasa']
                        monto_base = row['monto_base'] * row['tasa'] 
                        monto_cheque = monto_total - retenido
                        monto_sustraendo= monto_sustraendo * row['tasa']
                    else: 
                        monto_total= row['monto_total']
                        monto_base = row['monto_base'] * row['tasa'] 
                        monto_cheque = monto_total - retenido
                        monto_sustraendo= monto_sustraendo * row['tasa']


                    final.append({
                        'comprobante': row['comprobante'],
                        'fecha': row['fecha'],
                        'proveedor': row['proveedor'],
                        'rif': row['rif'],
                        'porcentaje_islr': row['porcentaje_islr'],
                        'retenido': retenido,
                        'tipo_residencia': row['tipo_residencia'],
                        'descripcion': row['cod'],
                        'monto_sustraendo': monto_sustraendo,
                        'sustraendo': row['sustraendo'],
                        'factor': row['factor'],
                        'monto_cheque': monto_cheque,
                        'monto_total': monto_total,
                        'monto_base': monto_base,
                        })

            else: 

                for row in query_result:
                    monto_cheque = 0.00
                    monto_sustraendo = 0.00
                    retenido = row['retenido'] 
                    
                    if row['sustraendo'] == True:
                        if row['porcentaje_islr'] == 1:
                            monto_sustraendo = row['sus_1']
                        if row['porcentaje_islr'] == 3:
                            monto_sustraendo = row['sus_3']
                        #retenido = retenido - monto_sustraendo

                    if row['cod'] not in concepto:
                        concepto.append(row['cod'])
                    
                    if row['moneda'] == self.env.company.currency_id.id:
                        monto_total= row['monto_total'] 
                        monto_base = row['monto_base']
                        monto_cheque = monto_total - retenido
                        monto_sustraendo= monto_sustraendo
                    else: 
                        monto_total= row['monto_total'] / row['tasa']
                        monto_base = row['monto_base'] 
                        monto_cheque = monto_total - retenido
                        monto_sustraendo= monto_sustraendo 

                    final.append({
                        'comprobante': row['comprobante'],
                        'fecha': row['fecha'],
                        'proveedor': row['proveedor'],
                        'rif': row['rif'],
                        'porcentaje_islr': row['porcentaje_islr'],
                        'retenido': retenido,
                        'tipo_residencia': row['tipo_residencia'],
                        'descripcion': row['cod'],
                        'monto_sustraendo': monto_sustraendo,
                        'sustraendo': row['sustraendo'],
                        'factor': row['factor'],
                        'monto_cheque': monto_cheque,
                        'monto_total': monto_total,
                        'monto_base': row['monto_base'],
                        })         
        else:
            raise UserError(_("No hay datos para imprimir"))

        data = {
            'ids': self.ids,
            'model': self._name,
            'state': estatus_view if self.state else '',
            'final': final,
            'concepto': concepto,
            'date_start': self.date_start if self.date_start else '',
            'date_end': self.date_end if self.date_end else '',
            'partner_id': self.partner_id.rif+' '+self.partner_id.name if self.partner_id else '',
            'move_type': self.move_type,
        }

        return self.env.ref('eu_reporte_islr.islr_report').report_action(self, data=data)

