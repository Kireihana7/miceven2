from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()

class IncidenceCreator(models.Model):
    _name = 'incidence.line'
    _inherit=['mail.thread', 'mail.activity.mixin']

    def get_date_ini(self):
            try:
                return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).date_start
            except:
                return False
    def get_date_fin(self):
            try:
                return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).date_end
            except:
                return False
    def get_date_category_id(self):
            try:
                    return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).category_id_filter
            except:
                return False
    state=fields.Selection([('open','Abierto'),('closed','Cerrado')],string="Estado",tracking=True,default="open")

    employee_ids=fields.Many2many('hr.employee',string="Empleados",required=True,tracking=True)
    work_entry_type=fields.Many2one('hr.work.entry.type','Tipo de entrada',required=True,tracking=True)
    fecha_ini=fields.Date(string="fecha inicio lote",required=True,default=get_date_ini,tracking=True)
    fecha_fin=fields.Date(string="fecha fin lote",required=True,default=get_date_fin,tracking=True)
    category_id=fields.Many2one('hr.employee.category',string="Categoria",default=get_date_category_id,tracking=True)
    hours_or_days=fields.Selection([('hour','Horas'),('day','Días')],string="Unid. de tiempo",required=True,tracking=True)
    number_of_unit=fields.Float(string="Cantidad",required=True,tracking=True)


    def button_state(self):
        for rec in self:
            if rec.state=='open':
                rec.state="closed"
            else:
                rec.state="open"
    @api.constrains('fecha_fin')
    def contrain_fecha_fin(self):
        for rec in self:
            if rec.fecha_fin<rec.fecha_ini:
                raise UserError ('La fecha fin no puede ser menor a la fecha inicio')
    @api.constrains('fecha_ini')
    def contrain_fecha_ini(self):
        for rec in self:
            if rec.fecha_fin<rec.fecha_ini:
                raise UserError ('La fecha fin no puede ser menor a la fecha inicio')
    @api.constrains('number_of_unit')
    def contrain_units(self):
        for rec in self:
            if (rec.hours_or_days=="day" and rec.number_of_unit > (rec.fecha_fin-rec.fecha_ini).days+1) or (rec.hours_or_days=="hour" and rec.number_of_unit > ((rec.fecha_fin-rec.fecha_ini).days*24)+24):
                raise UserError ('No creo que debas colocar un periodo de tiempo mayor al posible dado el periodo')
    @api.constrains('work_entry_type')
    def validate_incidence_duplex(self):
        for rec in self:
            duplicates=self.env['incidence.line'].search([('category_id','=',rec.category_id.id),('fecha_ini','=',rec.fecha_ini),('fecha_fin','=',rec.fecha_fin),('employee_ids','in',rec.employee_ids.ids),('work_entry_type','=',rec.work_entry_type.id),('id','!=',rec.id)])
            if duplicates:
                raise UserError ("No puede tener incidencias repetidas para este empleado en un misma rango de fecha y categoria")

