# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

# class StockPicking(models.Model):
#     _inherit = 'stock.picking'

#     partner_id  = fields.Many2one(track_visibility="always")
#     picking_type_id = fields.Many2one(track_visibility="always")
#     location_id         = fields.Many2one(track_visibility="always")
#     user_id         = fields.Many2one(track_visibility="always")
#     product_id   = fields.Many2one(track_visibility="always")
#     location_dest_id     = fields.Many2one(track_visibility="always")
#     scheduled_date          = fields.Datetime(track_visibility="always")
#     origin = fields.Char(track_visibility="always")
#     move_type = fields.Selection(track_visibility="always")
#     product_uom = fields.Many2one(track_visibility="always")
#     analytic_account_id = fields.Many2one(track_visibility="always")
#     analytic_tag_ids = fields.Many2many(track_visibility="always")

class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    user_id = fields.Many2one(track_visibility="always")
    picking_type_id = fields.Many2one(track_visibility="always")
    company_id = fields.Many2one(track_visibility="always")
    scheduled_date          = fields.Datetime(track_visibility="always")


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    location_ids = fields.Many2many(tracking=True)
    product_ids = fields.Many2many(tracking=True)
    exhausted = fields.Boolean(tracking=True)
    accounting_date = fields.Date(tracking=True)
    company_id = fields.Many2one(tracking=True)
    prefill_counted_quantity = fields.Selection(tracking=True)

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    user_id = fields.Many2one(track_visibility="always")
    picking_type_id = fields.Many2one(track_visibility="always")
    company_id = fields.Many2one(track_visibility="always")
    scheduled_date          = fields.Datetime(track_visibility="always")
    product_uom_id = fields.Many2one(track_visibility="always")
    analytic_account_id = fields.Many2one(track_visibility="always")
    analytic_tag_ids = fields.Many2many(track_visibility="always")
    package_id = fields.Many2one(track_visibility="always")
    owner_id = fields.Many2one(track_visibility="always")
    company_id = fields.Many2one(track_visibility="always")


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_id = fields.Many2one(track_visibility="always")
    product_qty = fields.Float(track_visibility="always")
    ref = fields.Char(track_visibility="always")



class ProductTemplate(models.Model):
    _inherit ='product.template'

    type = fields.Selection(track_visibility="always")
    categ_id = fields.Many2one(track_visibility="always")
    default_code = fields.Char(track_visibility="always")
    barcode = fields.Char(track_visibility="always")
    list_price = fields.Float(track_visibility="always")
    taxes_id = fields.Many2many(track_visibility="always")
    standard_price = fields.Float(track_visibility="always")
    uom_id = fields.Many2one(track_visibility="always")
    uom_po_id = fields.Many2one(track_visibility="always")
    invoice_policy = fields.Selection(track_visibility="always")
    expense_policy  = fields.Selection(track_visibility="always")     
    purchase_method = fields.Selection(track_visibility="always")
    supplier_taxes_id = fields.Many2many(track_visibility="always")
    route_ids = fields.Many2many(track_visibility="always")
    tracking = fields.Selection(track_visibility="always")
    responsible_id = fields.Many2one(track_visibility="always")
    weight = fields.Float(track_visibility="always")
    volume = fields.Float(track_visibility="always")
    produce_delay = fields.Float(track_visibility="always")
    sale_delay = fields.Float(track_visibility="always")
    property_stock_production = fields.Many2one(track_visibility="always")
    property_stock_inventory = fields.Many2one(track_visibility="always")
    property_account_income_id = fields.Many2one(track_visibility="always")
    property_account_expense_id = fields.Many2one(track_visibility="always")
    property_account_creditor_price_difference = fields.Many2one(track_visibility="always")





