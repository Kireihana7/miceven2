# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = 'res.users'

    menu_ids = fields.Many2many('ir.ui.menu', 'user_menu_rel', 'user_id', 'menu_id', string='Menú a ocultar', help='Seleccionar menú para ocultar a este usuario')
    report_ids = fields.Many2many('ir.actions.report', 'user_report_rel', 'user_id', 'report_id', 'Reporte a ocultar',
                                  help='Seleccionar reporte para ocultar a este usuario')

    # Earlier Needs to restart server to take invisible effect
    # After User Request added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(Users, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(Users, self).write(values)


class ResGroups(models.Model):
    _inherit = 'res.groups'

    menu_ids = fields.Many2many('ir.ui.menu', 'group_menu_rel', 'group_id', 'menu_id', string='Menú a ocultar')
    report_ids = fields.Many2many('ir.actions.report', 'group_report_rel', 'group_id', 'report_id', 'Reporte a ocultar',
                                  help='Seleccionar reporte para ocultar a este usuario')

    # Earlier Needs to restart server to take invisible effect
    # After User Request added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(ResGroups, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(ResGroups, self).write(values)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    hide_user_ids = fields.Many2many('res.users', 'user_report_rel', 'report_id', 'user_id', string='Ocultar a usuarios')
    hide_group_ids = fields.Many2many('res.groups', 'group_report_rel', 'report_id', 'group_id', string='Ocultar a grupos')


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    hide_group_ids = fields.Many2many('res.groups', 'group_menu_rel', 'menu_id', 'group_id', string='Ocultar a grupos')
    hide_user_ids = fields.Many2many('res.users', 'user_menu_rel', 'menu_id', 'user_id', string='Ocultar a usuarios')

    # Earlier Needs to restart server to take invisible effect
    # After User Request added clear cache code so no need to restart server
    @api.model
    def create(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).create(values)

    def write(self, values):
        self.env['ir.ui.menu'].clear_caches()
        return super(IrUiMenu, self).write(values)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user == self.env.ref('base.user_root'):
            return super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
        else:
            menus = super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
            if menus:
                menu_ids = [menu for menu in self.env.user.menu_ids]
                menu_ids2 = [menu for group in self.env.user.groups_id for menu in group.menu_ids]
                for menu in list(set(menu_ids).union(menu_ids2)):
                    if menu in menus:
                        menus -= menu
                if offset:
                    menus = menus[offset:]
                if limit:
                    menus = menus[:limit]
            return len(menus) if count else menus

class IrModel(models.Model):
    _inherit = 'ir.model'

    field_configuration_ids = fields.One2many('field.configuration', 'model_id', string='Field Configuration')



class FieldConfiguration(models.Model):
    _name = 'field.configuration'
    _description = 'Field Configuration'

    model_id = fields.Many2one('ir.model', string='Módelo', required=True,ondelete='cascade',)
    field_id = fields.Many2one('ir.model.fields', string='Campo', required=True,ondelete='cascade',)
    field_name = fields.Char(related='field_id.name', string='Nombre Ténico', readonly=True)
    group_ids = fields.Many2many('res.groups', 'field_config_group_rel', 'group_id', 'field_config_id', required=True, string='Grupos')
    readonly = fields.Boolean('ReadOnly', default=False)
    invisible = fields.Boolean('Invisible', default=False)

    #_sql_constraints = [
    #    ('field_model_readonly_unique', 'UNIQUE ( field_id,  readonly)',
    #     _('Readonly Attribute Is Already Added To This Field, You Can Add Group To This Field!')),
    #    ('model_field_invisible_uniq', 'UNIQUE ( field_id, invisible)',
    #     _('Invisible Attribute Is Already Added To This Field, You Can Add Group To This Field'))
    #]
