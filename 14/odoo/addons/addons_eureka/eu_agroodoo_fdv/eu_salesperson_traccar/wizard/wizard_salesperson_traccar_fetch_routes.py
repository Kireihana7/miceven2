import requests
import json
import logging

from ast import literal_eval
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

class WizardTraccarFetchRoutes(models.TransientModel):
    _name = "wizard.salesperson.traccar.fetch.routes"
    _description = "Salesperson Traccar Fetch Routes Wizard"

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', 'Empleado', domain="[('is_traccar', '=', True)]")
    device_id = fields.Char(string='Device ID', help="Device ID")
    from_date = fields.Datetime(string='Date From', required=True, default=fields.Datetime.now, help="Date starting range for filter")
    to_date = fields.Datetime(string='Date To', required=True, default=fields.Datetime.now, help="Date end range for filter")
    
    @api.onchange('to_date','from_date')
    def onchange_date(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise UserError(_('End date must be greater than start date.'))

    def action_fetch_routes(self):
        to_date = self.to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        from_date = self.from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.env['salesperson.traccar.route.details'].sudo().cron_update_route_details(to_date, from_date)
        title = 'Message'
        message = _('Traccar Routes are successfully created')
        return self.env['salesperson.raise.message'].raise_message(message, title)