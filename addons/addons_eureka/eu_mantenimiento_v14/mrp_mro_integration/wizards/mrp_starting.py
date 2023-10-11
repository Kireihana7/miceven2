# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError




class MrpStarting(models.TransientModel):
    _inherit = 'mrp.starting'


    def do_starting(self):
        if self.workorder_id.workcenter_id.state == "on_maintenance":
            raise UserError(_('Workcenter %s is on maintenance') % self.workorder_id.workcenter_id.name)
        if self.workorder_id.milestone:
            workorders = self.production_id.workorder_ids
            sequence_milestone = self.workorder_id.sequence
            prev_workorders = [x for x in workorders if x.sequence < sequence_milestone]
            if any(prev_workorder.workcenter_id.state == 'on_maintenance' for prev_workorder in prev_workorders):
                raise UserError(_('at least one of previous workorders is on maintenance'))
        return super().do_starting()
