# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MrpMroRequestProductionWizard(models.TransientModel):
    _name = 'mrp.mro.request.production.wizard'
    _description = "MRP MRO Request Production Wizard"


    REQ_MAINTENANCE_TYPE_SELECTION = [
        ('bm', 'Corrective'),
        ('in', 'Inspection'),
        ('rf', 'Retrofit'),
    ]

    PRIORITY_SELECTION = [
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Breakdown')
    ]

    def _group_requested_by_domain(self):
        group = self.env.ref('mro_maintenance.group_maintenance_administrator', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []


    workcenter_id = fields.Many2one('mrp.workcenter', 'Workcenter', required=True)
    company_id = fields.Many2one('res.company', 'Company', related="production_id.company_id")
    maintenance_type = fields.Selection(REQ_MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', readonly=True, default="bm")
    cause = fields.Text('Cause', required=True)
    description = fields.Text('Description')
    requested_date = fields.Datetime('Requested Date', required=True)
    production_id = fields.Many2one('mrp.production', 'Production Order', readonly=True)
    requested_by = fields.Many2one('res.users', 'Requested by', domain=_group_requested_by_domain, required=True)
    maintenance_priority = fields.Selection(PRIORITY_SELECTION, 'Maintenance Priority', default='1', required=True)


    @api.onchange('production_id')
    def _get_workcenter_domain(self):
        if self.production_id:
            return {'domain': {'workcenter_id': [('id', 'in', self.production_id.workorder_ids.workcenter_id.ids)]}}

    @api.constrains('workcenter_id')
    def check_equipemnt_assignment(self):
        if not self.workcenter_id.equipment_id:
            raise UserError(_("no Equipment has been assigned to the workcenter"))
        return True


    @api.model
    def default_get(self, fields):
        default = super().default_get(fields)
        active_id = self.env.context.get('active_id', False)
        if active_id:
            default['production_id'] = active_id
        return default

    def action_mro_request_create(self):
        for record in self:
            mro_request_id = self.env['mro.request'].create({
                    'equipment_id': record.workcenter_id.equipment_id.id,
                    'maintenance_type': record.maintenance_type,
                    'cause': record.cause,
                    'description': record.description,
                    'requested_by': record.requested_by.id,
                    'requested_date': record.requested_date,
                    'maintenance_priority': record.maintenance_priority,
                    'production_id': record.production_id.id,
                })
        return True
