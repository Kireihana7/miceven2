# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class EmployeOrder(models.TransientModel):
    _name="employe.order"
    _description='Employe Order'

    employe_id = fields.Many2one('hr.employee', string='Employee')
    start_date = fields.Date( string='From Date')
    to_date = fields.Date( string='To Date')

    #Open maintenance view function        
    def action_view(self):
        repair_date= self.env['maintenance.request'].search([('request_date','>=',self.start_date),('request_date','<=',self.to_date),("user_id",'=',self.employe_id.name)])
        if self.start_date > self.to_date:
            raise ValidationError("Date interval is invalid")
        elif not repair_date:
                    raise ValidationError("The maintenance has no request At this date interval ")   
        return { 
                'name': ('MaintenanceRequest'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'maintenance.request',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain':[('request_date','>=',self.start_date),('request_date','<=',self.to_date),("user_id",'=',self.employe_id.name)],
                }

    # Print Report Action
    def action_print(self):
        data = {}
        data['Employe_Order'] = self.env.context.get('active_id')
        action=  self.env.ref('abs_maintenance_summary.maintenance_order_report')\
            .with_context(discard_logo_check=True).report_action(self)
        action.update({'close_on_report_download':True})
        if self.start_date > self.to_date:
            raise ValidationError("Date interval is invalid")
        return action

    # Print Report Action
    def _print_report(self,data):
        return self.env.ref('abs_maintenance_summary.maintenance_order_report												').report_action(self, data=data, config=False)

