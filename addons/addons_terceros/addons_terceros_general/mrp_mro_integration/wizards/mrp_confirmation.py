# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MrpConfirmation(models.TransientModel):
    _inherit = 'mrp.confirmation'


    def do_confirm(self):
        for record in self:
            # workcenter on maintenance
            if record.workorder_id.workcenter_id.state == "on_maintenance":
                raise UserError(_('Workcenter %s is on maintenance') % record.workorder_id.workcenter_id.name)
            if record.workorder_id.milestone:
                workorders = record.production_id.workorder_ids
                sequence_milestone = record.workorder_id.sequence
                prev_workorders = [x for x in workorders if x.sequence < sequence_milestone]
                if any(prev_workorder.workcenter_id.state == 'on_maintenance' for prev_workorder in prev_workorders):
                    raise UserError(_('at least one of previous workorders is on maintenance'))
            # periodic maintenance
            if record.workorder_id.workcenter_id.periodic_maintenance:
                if not record.workorder_id.workcenter_id.equipment_id.meter_id:
                    raise UserError(_('No meter has been assigned to the equipment %s') % record.workorder_id.workcenter_id.equipment_id.name)
                if not record.workorder_id.workcenter_id.equipment_id.meter_id.measure_type == "delta":
                    raise UserError(_('The Measure Type for the meter %s has to be set as "delta"') % record.workorder_id.workcenter_id.meter_id.name)
                if not record.production_id.product_uom_id == record.workorder_id.workcenter_id.equipment_id.meter_id.meter_uom:
                    raise UserError(_('The UoM of the meter %s is different') % record.workorder_id.workcenter_id.meter_id.name)
                else:
                    mearure_line_id = self.env['mro.meter.line'].create({
                    'date': record.date_end,
                    'value': record.qty_output_wo,
                    'meter_id': record.workorder_id.workcenter_id.equipment_id.meter_id.id,
                })
        return super().do_confirm()


