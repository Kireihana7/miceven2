# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def share_so(self):
        action = self.env.ref('portal.portal_share_action').read()[0]
        action['context'] = {'active_id': self.id,
                             'active_model': self._name}
        return action

