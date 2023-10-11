# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class ResUsers(models.Model):
    _inherit = 'res.users'


    #property_warehouse_id = fields.Many2many('stock.warehouse', string='Default Warehouse', )


    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')

    #def _get_default_warehouse_id(self):
    #    if self.property_warehouse_id:
    #        return self.property_warehouse_id
    #    # !!! Any change to the following search domain should probably
    #    # be also applied in sale_stock/models/sale_order.py/_init_column.
    #    return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    #def __init__(self, pool, cr):
    #    """ Override of __init__ to add access rights.
    #        Access rights are disabled by default, but allowed
    #        on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
    #    """

    #    sale_stock_writeable_fields = [
    #        'property_warehouse_id',
    #    ]

    #    init_res = super().__init__(pool, cr)
    #    # duplicate list to avoid modifying the original reference
    #    type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + sale_stock_writeable_fields
    #    type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + sale_stock_writeable_fields
    #    return init_res


class stock_move(models.Model):
    _inherit = 'stock.move'
    @api.constrains('state', 'location_dest_id')
    def check_user_location_rights(self):
        for rec in self:
            if rec.state != 'done':
                return True
            user_locations = self.env.user.stock_location_ids
            print(user_locations)
            print("Checking access %s" %self.env.user.default_picking_type_ids)
            if self.env.user.restrict_locations:
                message = _(
                    'Ubicación No Permitida. No puedes procesar movimientos de esta ubicación '
                    ' "%s". '
                    'Por favor, contacte con su administrador.')
                if rec.location_id not in user_locations:
                    raise Warning(message % rec.location_id.name)
                elif rec.location_dest_id not in user_locations:
                    raise Warning(message % rec.location_dest_id.name)


