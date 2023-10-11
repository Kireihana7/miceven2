# -*- coding: utf-8 -*-


from odoo import models, fields, api, _



class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'


    wc_state = fields.Selection(string='WC Status', related='workcenter_id.state')