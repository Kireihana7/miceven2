# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import ValidationError


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('key') in ['mail.bounce.alias', 'mail.catchall.alias']:
<<<<<<< HEAD
                vals['value'] = self.env['mail.alias']._clean_and_check_unique([vals.get('value')])[0]
=======
                vals['value'] = self.env['mail.alias']._clean_and_check_unique(vals.get('value'))
            elif vals.get('key') == 'mail.catchall.domain.allowed':
                vals['value'] = vals.get('value') and self._clean_and_check_mail_catchall_allowed_domains(vals['value'])
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return super().create(vals_list)

    def write(self, vals):
        for parameter in self:
            if 'value' in vals and parameter.key in ['mail.bounce.alias', 'mail.catchall.alias'] and vals['value'] != parameter.value:
<<<<<<< HEAD
                vals['value'] = self.env['mail.alias']._clean_and_check_unique([vals.get('value')])[0]
        return super().write(vals)

    @api.model
    def set_param(self, key, value):
        if key == 'mail.restrict.template.rendering':
            group_user = self.env.ref('base.group_user')
            group_mail_template_editor = self.env.ref('mail.group_mail_template_editor')

            if not value and group_mail_template_editor not in group_user.implied_ids:
                group_user.implied_ids |= group_mail_template_editor

            elif value and group_mail_template_editor in group_user.implied_ids:
                # remove existing users, including inactive template user
                # admin will regain the right via implied_ids on group_system
                group_user._remove_group(group_mail_template_editor)
        # sanitize and normalize allowed catchall domains
        elif key == 'mail.catchall.domain.allowed' and value:
            value = self.env['mail.alias']._clean_and_check_mail_catchall_allowed_domains(value)

        return super(IrConfigParameter, self).set_param(key, value)
=======
                vals['value'] = self.env['mail.alias']._clean_and_check_unique(vals.get('value'))
            elif 'value' in vals and parameter.key == 'mail.catchall.domain.allowed' and vals['value'] != parameter.value:
                vals['value'] = vals['value'] and self._clean_and_check_mail_catchall_allowed_domains(vals['value'])
        return super().write(vals)

    def _clean_and_check_mail_catchall_allowed_domains(self, value):
        """ The purpose of this system parameter is to avoid the creation
        of records from incoming emails with a domain != alias_domain
        but that have a pattern matching an internal mail.alias . """
        value = [domain.strip().lower() for domain in value.split(',') if domain.strip()]
        if not value:
            raise ValidationError(_("Value for `mail.catchall.domain.allowed` cannot be validated.\n"
                                    "It should be a comma separated list of domains e.g. example.com,example.org."))
        return ",".join(value)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
