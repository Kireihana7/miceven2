from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.tools import safe_eval

class HrAttendanceGeofence(models.Model):
    _name = "hr.attendance.geofence"
    _description = "Attendance Geofence"
    _order = "id desc"
    
    name = fields.Char('Name', required=True)
    description = fields.Char('Description')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    employee_ids = fields.Many2many('hr.employee', 'employee_geofence_rel', 'geofence_id', 'emp_id', string='Employees')
    overlay_paths = fields.Text(string='Paths')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.model
    def create(self, vals_list):
        return super().create(vals_list)
    
    def auto_create(self, vals_list, user_id):
        # Obteniendo el employee por el user_id asociado
        geofence_sequence = self.env['ir.sequence'].next_by_code('auto.geofence.sequence')
        vals_list['name'] = f"{geofence_sequence}: {vals_list['name']}"
        employee_obj = self.env['hr.employee'].search([('user_id', '=', user_id)])
        if not employee_obj:
            raise exceptions.UserError('No existe un empleado relacionado al comercial.')
        vals_list['employee_ids'] = [employee_obj.id]
        
        # Verfificando si ya existe una Geocerca para este contacto
        partner_obj = self.env['res.partner'].browse(vals_list['partner_id'])
        
        # Agregando la nueva geocerca al contacto
        res = self.create(vals_list)
        partner_obj.geofence_location_id = res.id
        return "Geocerca creado satisfactoriamente."