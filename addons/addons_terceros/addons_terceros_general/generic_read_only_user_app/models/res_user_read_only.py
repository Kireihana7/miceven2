# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_
from odoo.exceptions import Warning

SAFELIST = [
    'res.users.log',
    'res.users',
    'res.config.settings',
    'mail.channel',
    'mail.alias',
    'bus.presence',
    'res.lang',
    "res.partner",
    "res.company",
    "ir.sequence",
    "mail.compose.message",
    "res.branch",
    "registrar.hallazgo",
    "alternar.hallazgo",
    "mail.message",
    "mail.thread"
    "ir.module.module",
    "ir.attachment",
    "mail.wizard.invite",
    #"base.module.update",
    #"ir.module.module",
]

class ResUser(models.Model):
    _inherit = 'res.users'

    read_only = fields.Boolean("Make Read Only")
    
    @api.onchange('read_only')
    def onchange_read_only(self):
        read_only_grp_id = self.env['ir.model.data'].get_object_reference('generic_read_only_user_app', 'group_read_only_user')[1]

        for rec in self:
            group_ids: list = rec.groups_id.ids

            if not rec.read_only:
                group_ids.append(read_only_grp_id)
            else:
                group_ids.remove(read_only_grp_id)

            rec.write({'groups_id': ([(6, 0, group_ids)])})

            rec.read_only = not rec.read_only

class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        result = super().check(model=model, mode=mode, raise_exception=raise_exception)

        if self.env.user.has_group('generic_read_only_user_app.group_read_only_user'):
            if not any([
                model.startswith("custom.audit"),
                model.startswith("material.purchase"),
                model.startswith("survey."),
            ]) and (model not in SAFELIST):
                if mode != 'read':
                    return False

        return result

class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _compute_domain(self, model_name, mode="read"):
        res = super()._compute_domain(model_name, mode)

        if self.env.user.has_group('generic_read_only_user_app.group_read_only_user'):
            if not any([
                model_name.startswith("custom.audit"),
                model_name.startswith("material.purchase"),
                model_name.startswith("survey."),
            ])  and (model_name not in SAFELIST):
                if mode != 'read':
                    raise Warning(
                        _('Read only user can not done this operation..! ' + model_name)
                    )
            
        return res