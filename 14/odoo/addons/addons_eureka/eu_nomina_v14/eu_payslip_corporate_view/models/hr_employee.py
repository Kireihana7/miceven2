# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date,timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange


TODAY=date.today()

class HrEmployeeEu(models.Model):
    _inherit = 'hr.employee'

    secret_journey=fields.Many2one('resource.calendar',string="Jornada oculta")
    def action_go_to_prestaciones_corporate(self):

        return {
            'type':'ir.actions.act_window',
            'name': 'Prestaciones del trabajador',
            'res_model':'hr.prestaciones.corporate.employee.line',
            'domain':[('parent_id','=',self.id)],
            'view_mode':'tree',
            'target':'current'
        }


    puntual=fields.Boolean("Puntual",tracking=True,compute="_compute_exemplarity",store=True,readonly=False)
    exemplar=fields.Boolean("Ejemplar",tracking=True,compute="_compute_exemplarity",store=True,readonly=False)

    @api.depends('slip_ids','attendance_ids','last_attendance_id.check_out','last_attendance_id.delay_hours','last_attendance_id.early_leave_hours')
    def _compute_exemplarity(self):
        for rec in self:
            now=datetime.now()
            last_week=now-relativedelta(day=7)
            rec.puntual=True
            rec.exemplar=True
            last_seven_days=rec.attendance_ids.filtered(lambda x: now>=x.check_in>=last_week)
            if last_seven_days :
                if (sum(last_seven_days.mapped('early_leave_hours'))+sum(last_seven_days.mapped('delay_hours')))<3:
                    rec.puntual=True
                    rec.exemplar=True
                elif (sum(last_seven_days.mapped('early_leave_hours'))+sum(last_seven_days.mapped('delay_hours')))<10:
                    rec.puntual=True
                    rec.exemplar=False
                else:
                    rec.puntual=False
                    rec.exemplar=False
            
class HrEmployeeEuP(models.Model):
    _inherit = 'hr.employee.public'

    secret_journey=fields.Many2one('resource.calendar',string="Jornada oculta")
   


class HrPrestacionLines(models.Model):
    _name = "hr.prestaciones.corporate.employee.line"
    its_super_secret=fields.Boolean(string="Shh", groups="eu_payslip_corporate_view.corporate_super_payslip_group",compute="_compute_secret")
    name=fields.Char(compute="_naming_the_p_line")
    comprometida=fields.Boolean(string="Comprometida para pago")
    line_type=fields.Selection([('prestacion','prestacion'),('anticipo','anticipo'),('liquidacion','liquidacion'),('clean','clean')])
    parent_id=fields.Many2one('hr.employee')
    company_id=fields.Many2one('res.company',default=lambda self: self.env.company)
    fecha=fields.Date()
    contract_id=fields.Many2one('hr.contract')
    sal_mensual=fields.Float("saldo mensual")
    sal_diario=fields.Float("saldo diario")
    antiguedad=fields.Float()
    antiguedad_adicional=fields.Float()
    utilidades=fields.Float()
    vacaciones=fields.Float()
    antiguedad80=fields.Float()
    total_diario=fields.Float()
    prestaciones_mes=fields.Float()
    anticipos_otorga=fields.Float()
    porcentaje=fields.Float(string="%")
    prestaciones_acu=fields.Float(string="prest. acum.")
    tasa_activa=fields.Float()
    intereses=fields.Float()
    intereses_acum=fields.Float(string="int. acum.")
    presta_e_inte=fields.Float(string="Acum.")
    parent_lote_prest=fields.Many2one('hr.prestaciones.corporate')
    parent_lote_anticip=fields.Many2one('hr.anticipos.corporate')
    is_anticipo_intereses=fields.Boolean()

    @api.depends("parent_lote_anticip","parent_lote_anticip.its_super_secret","parent_lote_prest","parent_lote_prest.its_super_secret")
    def _compute_secret(self):
        for rec in self:
            if rec.parent_lote_prest.its_super_secret or rec.parent_lote_anticip.its_super_secret:
                rec.its_super_secret=True
            else:
                rec.its_super_secret=False
    @api.depends("parent_id",'fecha')
    def _naming_the_p_line(self):
        for rec in self:
            rec.name=f"Linea estado de prestaciones de {rec.parent_id.name} para el {rec.fecha}"

# class HrAttendanceRemix(models.AbstractModel):
#     _inherit="hr.employee.base"

# def create_work_entry_from_attendance(self,attendance):
#          if attendance.check_out !=False and self.env['ir.config_parameter'].sudo().get_param('l10n_ve_payroll.create_work_entry_with_attendance'):
#             entrace=self.env['hr.work.entry'].sudo().create({
#                 'name':f"Asistencia : {attendance.employee_id.name}",
#                 'employee_id':attendance.employee_id.id,
#                 'date_start':attendance.check_in,
#                 'date_stop':attendance.check_out,
#                 'duration':attendance.worked_hours,
#                 'work_entry_type_id':self.env['hr.work.entry.type'].search([('code','=','WORK100')],limit=1).id
#             })
#             entrace._compute_dias_feriados_laborados()


