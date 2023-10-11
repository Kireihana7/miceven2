# -*- coding: utf-8 -*-


from itertools import zip_longest
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare


class MrpDemandCreateTool(models.TransientModel):
    _name = "mrp.demand.create.tool"
    _description = "MRP Demand Create Tool"

    date_start = fields.Date("Date From", required=True)
    date_end = fields.Date("Date To", required=True)
    date_range_type_id = fields.Many2one("date.range.type", "Date Range Type", required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)
    product_ids = fields.Many2many("product.product", string="Products", domain="[('type', '=', 'product')]", required=True)


    @api.constrains("date_start", "date_end")
    def _check_start_end_dates(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be later than the end date."))
        return True

    @api.constrains("product_ids", "warehouse_id")
    def _check_mrp_parameter(self):
        if not self.product_ids:
            raise UserError(_("Enter at least one product."))
        for product in self.product_ids:
            mrp_parameter =self.env['mrp.parameter'].search([('product_id', '=', product.id), ('warehouse_id', '=', self.warehouse_id.id)], limit=1)
            if not mrp_parameter:
                raise UserError(_("MRP Parameter master data has not been created for the product '%s'.")% product.name)
        return True

    def create_sheet(self):
        self.ensure_one()
        sheet = self.env["mrp.demand.create.sheet"].create({
                "date_start": self.date_start,
                "date_end": self.date_end,
                "warehouse_id": self.warehouse_id.id,
                "date_range_type_id": self.date_range_type_id.id,
                "product_ids": [(6, 0, self.product_ids.ids)],
            })
        sheet._onchange_dates()
        return {
            "name": _("MRP Independent Demand Sheet"),
            "view_mode": "form",
            "target": "current",
            "res_model": "mrp.demand.create.sheet",
            "res_id": sheet.id,
            "type": "ir.actions.act_window",
        }

class MrpDemandCreateSheet(models.TransientModel):
    _name = "mrp.demand.create.sheet"
    _description = "MRP Demand Create Sheet"

    date_start = fields.Date("Date From", readonly=True)
    date_end = fields.Date("Date to", readonly=True)
    date_range_type_id = fields.Many2one("date.range.type", "Date Range Type", readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)
    product_ids = fields.Many2many("product.product", string="Product")
    line_ids = fields.Many2many("mrp.demand.create.sheet.line", string="MRP Demand Items")

    def name_get(self):
        result = []
        for record in self:
            rec_name = "MRP Demand Create Sheet"
            result.append((record.id, rec_name))
        return result

    @api.onchange("date_start", "date_end", "date_range_type_id")
    def _onchange_dates(self):
        if not all([self.date_start, self.date_end, self.date_range_type_id]):
            return
        ranges = self._get_ranges()
        if not ranges:
            raise UserError(_("There is no date range created."))
        lines = []
        warehouse = self.warehouse_id
        for product in self.product_ids:
            for d_range in ranges:
                date_start = fields.Datetime.from_string(d_range.date_start)
                date_end = fields.Datetime.from_string(d_range.date_end)
                items = self.env["mrp.demand"].search([
                    ("product_id", "=", product.id),
                    ("date_planned", ">=", date_start),
                    ("date_planned", "<", date_end),
                    ("warehouse_id", "=", warehouse.id),
                    ("state", "=", "draft"),
                ])
                if items:
                    uom_qty = sum(items.mapped("planned_qty"))
                    item_ids = items.ids
                else:
                    uom_qty = 0.0
                    item_ids = []
                lines.append([0, 0, self._get_default_sheet_line(d_range, product, warehouse, uom_qty, item_ids)])
        self.line_ids = lines

    def _get_ranges(self):
        domain_1 = [
            "&",
            ("type_id", "=", self.date_range_type_id.id),
            "|",
            "&",
            ("date_start", ">=", self.date_start),
            ("date_start", "<=", self.date_end),
            "&",
            ("date_end", ">=", self.date_start),
            ("date_end", "<=", self.date_end),
        ]
        domain_2 = [
            "&",
            ("type_id", "=", self.date_range_type_id.id),
            "&",
            ("date_start", "<=", self.date_start),
            ("date_end", ">=", self.date_start),
        ]
        domain = expression.OR([domain_1, domain_2])
        ranges = self.env["date.range"].search(domain)
        return ranges

    def _get_default_sheet_line(self, d_range, product_id, warehouse_id, uom_qty, item_ids):
        name_y = "{} - {}".format(product_id.display_name, product_id.uom_id.name)
        values = {
            "value_x": d_range.name,
            "value_y": name_y,
            "date_range_id": d_range.id,
            "product_id": product_id.id,
            "warehouse_id": warehouse_id.id,
            "product_qty": uom_qty,
            "demand_ids": [(6, 0, item_ids)],
        }
        return values

    @api.model
    def _prepare_demand_management_data(self, line, qty):
        date_planned = fields.Datetime.from_string(line.date_range_id.date_start)
        mrp_parameter = self.env['mrp.parameter'].search([('warehouse_id', '=', self.warehouse_id.id), ('product_id', '=', line.product_id.id)], limit=1)
        return {
            "mrp_parameter_id": mrp_parameter.id,
            "date_planned": date_planned,
            "planned_qty": qty,
        }

    def button_validate(self):
        res_ids = []
        for line in self.line_ids:
            quantities = []
            qty_to_order = line.product_qty
            while qty_to_order > 0.0:
                qty = qty_to_order
                quantities.append(qty)
                qty_to_order -= qty
            rounding = line.product_id.uom_id.rounding
            for proposed, current in zip_longest(quantities, line.demand_ids):
                if not proposed:
                    #current.unlink()
                    current.button_cancel()
                    current.filtered(lambda r: r.state == 'cancel').unlink()
                elif not current:
                    data = self._prepare_demand_management_data(line, proposed)
                    item = self.env["mrp.demand"].create(data)
                    res_ids.append(item.id)
                elif (float_compare(proposed, current.planned_qty, precision_rounding=rounding) == 0):
                    res_ids.append(current.id)
                else:
                    current.planned_qty = proposed
                    res_ids.append(current.id)

        return {
            "domain": [("id", "in", res_ids)],
            "name": _("MRP Demand Items"),
            "view_mode": "tree,form,pivot",
            "res_model": "mrp.demand",
            "type": "ir.actions.act_window",
        }


class MrpDemandCreateSheetLine(models.TransientModel):
    _name = "mrp.demand.create.sheet.line"
    _description = "MRP Demand Create Sheet Line"

    demand_ids = fields.Many2many("mrp.demand")
    product_id = fields.Many2one("product.product", "Product")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    date_range_id = fields.Many2one("date.range", "Date Range",)
    value_x = fields.Char("Period")
    value_y = fields.Char("Product")
    product_qty = fields.Float("Quantity", digits='Product Unit of Measure')
