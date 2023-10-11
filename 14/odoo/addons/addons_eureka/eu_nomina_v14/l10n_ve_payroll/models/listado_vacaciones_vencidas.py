# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta,date
from dateutil import relativedelta
TODAY=date.today()
class ListVacation(models.Model):
    _name = 'list.vacation'

    employee_id=fields.Many2one('hr.employee',string="Empleado")
    fecha_ingreso=fields.Date(related="employee_id.fecha_inicio",string="Fecha de ingreso")
    periodo_ini=fields.Date(string="Inicio del periodo correspondiente",store=True, compute="_compute_periodo")
    periodo_fin=fields.Date(string="Final del periodo correspondiente",store=True, compute="_compute_periodo")
    corresponde_a=fields.Integer(string="Año correspondiente",store=True, compute="_compute_periodo")
    company_id=fields.Many2one("res.company",default=lambda self: self.env.company,tracking=True)
    total=fields.Float(string="a pagar",compute="create_proyection",store=True)
    disfrutada=fields.Boolean(string="Disfrutada",compute="_compute_disfrutada",store=True)
    @api.depends("employee_id",'fecha_ingreso')
    def _compute_periodo(self):
        for rec in self:
            
            vacaciones_totales=rec.env['list.vacation'].search([('employee_id','=',rec.employee_id.id),('id','!=',rec.id),('periodo_fin','!=',False)],limit=1,order="corresponde_a desc")
            if vacaciones_totales:
                rec.periodo_ini=vacaciones_totales.periodo_fin
                rec.periodo_fin=vacaciones_totales.periodo_fin+relativedelta.relativedelta(years=1)
                rec.corresponde_a=rec.periodo_fin.year
            else:
                rec.periodo_ini=rec.fecha_ingreso
                rec.periodo_fin=rec.periodo_ini+relativedelta.relativedelta(years=1)
                rec.corresponde_a=rec.periodo_fin.year

    @api.depends('employee_id','periodo_ini')
    def create_proyection(self):
        for rec in self:
            if rec.periodo_ini:
                try:
                    struct_id=self.env['hr.payroll.structure'].search([('struct_category','=','vacation'),('use_for_proyection','=',True),('company_id','in',[False,rec.env.company.id])],limit=1)
                    if struct_id:
                        vacanom=rec.env["hr.payslip"].create({
                                    'employee_id':rec.employee_id.id,
                                    'is_vacation':True,
                                    'date_from':rec.periodo_ini,
                                    'date_to':rec.periodo_ini+relativedelta.relativedelta(years=rec.company_id.dias_vac_base),
                                    'anno_vacaciones_designado':rec.corresponde_a,
                                    'contract_id':rec.employee_id.contract_id.id,
                                    'struct_id':struct_id.id,
                                    'pay_type':'deposito',
                                    'name': f"Vacaciones",
                                    'company_id':rec.company_id.id,
                                    'journal_id':struct_id.journal_id.id,
                                })
                        vacanom.action_refresh_from_work_entries()
                        vacanom._onchange_is_vacation()
                        vacanom.compute_sheet()
                        rec.total=vacanom.total_sum
                        vacanom.sudo().action_payslip_cancel()
                        vacanom.sudo().unlink()
                except:
                    pass
            else:
                rec.total=0

    @api.depends('employee_id','employee_id.slip_ids','employee_id.slip_ids.state')
    def _compute_disfrutada(self):
        for rec in self:
            nominas_vaciones=rec.employee_id.slip_ids.filtered(lambda x: (x.is_vacation and x.state not in ['cancel','draft'] and x.anno_vacaciones_designado==rec.corresponde_a) or (x.liquidation_id and x.anno_vacaciones_designado<=rec.corresponde_a))
            if nominas_vaciones:
                rec.disfrutada=True
            else:
                rec.disfrutada=False

    def create_single_nomina(self):
        self.ensure_one()

        return {
            'type':'ir.actions.act_window',
            'name': f"Nómina vacaciones {self.corresponde_a}",
            'res_model':'hr.payslip',
            'view_mode':'form',
            'context':{'default_is_vacation':True,'default_employee_id':self.employee_id.id,'default_date_from':TODAY,'default_anno_vacaciones_designado':self.corresponde_a},
            'target':'current'
        }