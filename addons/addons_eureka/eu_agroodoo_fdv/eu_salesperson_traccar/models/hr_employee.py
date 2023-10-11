from odoo import _, api, fields, models

import logging
from datetime import date
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_traccar = fields.Boolean("Rastrear?", default=False)
    traccar_device_uniqueid = fields.Char(string='Identificación del Dispositivo', help="Identificación del Dispositivo")
    traccar_device_id = fields.Char(string='Traccar Dispositivo ID', help="Traccar Dispositivo ID")
    traccar_device_status = fields.Selection([
        ('online', 'Conectado'),
        ('offline', 'Desconectado')
        ], string='Está en línea?', default="offline", help="Device Status")
    traccar_device_lastupdate = fields.Char(string='Última Actualización', help="Última Actualización")

    def sync_traccar_device(self):
        config = self.env['salesperson.traccar.config.settings'].sudo().search([('active', '=', True)], limit=1)
        devices = config.fetch_devices_info(uniqueId=self.traccar_device_uniqueid)
        if devices:
            for device in devices:
                self.write({
                    'traccar_device_id': device['id'],
                    'traccar_device_status': 'online' if device['status'] == 'online' else 'offline',
                    'traccar_device_lastupdate': device['lastUpdate'] or False
                })
        else:
            data = {
                "name": self.name,
                "uniqueId" : self.traccar_device_uniqueid,
            }
            device = config.create_device_info(data)
            if device:
                self.traccar_device_id = device
                self.traccar_device_status = 'offline'
        return True

    def action_open_device_summary(self):
        vals = {
            'employee_id':self.id,
            'device_id' : self.traccar_device_id,
        }
        summary = self.env['wizard.salesperson.traccar.device.summary'].create(vals)
        context = self._context or {}
        return {
            'name': ("Ver resumen del dispositivo"),
            'res_model': 'wizard.salesperson.traccar.device.summary',
            'view_id': self.env.ref('eu_salesperson_traccar.form_wizard_salesperson_traccar_device_summary').id,
            'res_id': summary.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',                                                
            'context': context,
            'nodestroy': True,
            'target': 'new',
        }

    def action_fetch_trips(self):
        vals = {
            'employee_id':self.id,
            'device_id' : self.traccar_device_id,
        }
        trips = self.env['wizard.salesperson.traccar.fetch.trips'].create(vals)
        context = self._context or {}
        return {
            'name': ("Buscar viajes"),
            'res_model': 'wizard.salesperson.traccar.fetch.trips',
            'view_id': self.env.ref('eu_salesperson_traccar.form_wizard_salesperson_traccar_fetch_trips').id,
            'res_id': trips.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',                                                
            'context': context,
            'nodestroy': True,
            'target': 'new',
        }
    
    def action_fetch_routes(self):
        vals = {
            'employee_id':self.id,
            'device_id' : self.traccar_device_id,
        }
        routes = self.env['wizard.salesperson.traccar.fetch.routes'].create(vals)
        context = self._context or {}
        return {
            'name': ("Obtener rutas"),
            'res_model': 'wizard.salesperson.traccar.fetch.routes',
            'view_id': self.env.ref('eu_salesperson_traccar.form_wizard_salesperson_traccar_fetch_routes').id,
            'res_id': routes.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',                                                
            'context': context,
            'nodestroy': True,
            'target': 'new',
        }
    
    def action_open_device_location(self):
        vals = {
            'employee_id':self.id,
            'device_id' : self.traccar_device_id,
        }
        location = self.env['wizard.salesperson.traccar.device.location'].create(vals)
        context = self._context or {}
        return {
            'name': ("Ubicación del Dispositivo"),
            'res_model': 'wizard.salesperson.traccar.device.location',
            'view_id': self.env.ref('eu_salesperson_traccar.form_wizard_salesperson_traccar_device_location').id,
            'res_id': location.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',                                                
            'context': context,
            'nodestroy': True,
            'target': 'new',
        }

    @api.model
    def get_loc_clients(self, employee_id):
        employee_obj = self.browse(employee_id)
        if not employee_obj or not employee_obj.is_traccar:
            return
        user_id = employee_obj.user_id.id
        query = f"""
            SELECT 
                rp.name, 
                rp.partner_longitude AS long, 
                rp.partner_latitude AS lat
            FROM res_partner rp
            JOIN res_visit rv ON rv.partner_id = rp.id 
            WHERE rp.user_id = {user_id}
            AND rv.fecha_visita = '{date.today()}'
        """
        self._cr.execute(query)
        locations = self._cr.dictfetchall()
        for loc in locations:
            loc['coords'] = f"{loc['long']}, {loc['lat']}"
        return locations
