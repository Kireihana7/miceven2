from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrListActiveLeaveWiz(models.TransientModel):
    _name="hr.active.leave.list.wiz"
    _description="wizard for lists of active and gone employees"

    from_date=fields.Date("Desde")
    to_date=fields.Date("Hasta")
    type_selector=fields.Selection([('present','Presente Ahora (Asistencia)'),('active','Personal Activo'),('added','Personal Ingresado'),('terminated','Personal Egresado'),('on_vacation','De Vacaciones'),('leavism','Ausentismo')],required=True,default="active")


    def printo(self):
        if self.type_selector=="active":
            employees=self.env['hr.employee'].search([])
        elif self.type_selector=="present":
            employees=self.env['hr.employee'].search([('attendance_state','=','checked_in')])
        elif self.type_selector=="terminated":
            employees=self.env['hr.employee'].with_context(active_test=False).search([('active','=',False),('fecha_fin','<=',self.to_date),('fecha_fin','>=',self.from_date)])
        else:
            employees=self.env['hr.employee'].search([('fecha_inicio','<=',self.to_date),('fecha_inicio','>=',self.from_date)])


        return self.env.ref('l10n_ve_payroll.action_report_listado_personal').report_action(self)
