# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'group_id'])
        return [(template.id, '%s%s' % (template.group_id.display_name and '%s - ' % template.group_id.display_name or '', template.name or ''))
                for template in self]

