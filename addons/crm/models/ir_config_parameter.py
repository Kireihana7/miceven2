# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
<<<<<<< HEAD
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def write(self, vals):
        result = super(IrConfigParameter, self).write(vals)
        if any(record.key == "crm.pls_fields" for record in self):
<<<<<<< HEAD
            self.env.flush_all()
=======
            self.flush()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            self.env.registry.setup_models(self.env.cr)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super(IrConfigParameter, self).create(vals_list)
        if any(record.key == "crm.pls_fields" for record in records):
<<<<<<< HEAD
            self.env.flush_all()
=======
            self.flush()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            self.env.registry.setup_models(self.env.cr)
        return records

    def unlink(self):
        pls_emptied = any(record.key == "crm.pls_fields" for record in self)
        result = super(IrConfigParameter, self).unlink()
<<<<<<< HEAD
        if pls_emptied and not self._context.get(MODULE_UNINSTALL_FLAG):
            self.env.flush_all()
            self.env.registry.setup_models(self.env.cr)
        return result
=======
        if pls_emptied:
            self.flush()
            self.env.registry.setup_models(self.env.cr)
        return pls_emptied
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
