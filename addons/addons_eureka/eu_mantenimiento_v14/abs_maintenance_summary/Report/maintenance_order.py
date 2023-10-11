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
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class RepairReport(models.AbstractModel):
    _name = 'report.abs_maintenance_summary.maintenance_order'
    _description = "Maintenance summary"

    #Get maintenance report value function
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env['employe.order']
        if docids:
            active_id = docids
            docs = self.env['employe.order'].browse(docids)
            if docs:
                repair_ids = self.env['maintenance.request'].search([('request_date','>=',docs.start_date),('request_date','<=',docs.to_date),("user_id",'=',docs.employe_id.name)])
                if not repair_ids:
                    raise ValidationError("The maintenance  has no request At this date interval ")  
               
        return {
                   'doc_ids': repair_ids,
                   'doc_model': self.model,
                   'docs': docs,
                   }
