# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import date, datetime, timedelta


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    #new
    qty_done = fields.Float()
    product_uom_id = fields.Many2one(comodel_name="uom.uom")
    #new
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            if rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Datetime()
    date_to = fields.Datetime()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")
    #new
    location_dest_id = fields.Many2one(comodel_name="stock.location")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_today= datetime.now()
        date_top_from=datetime(1900,1,1,0,0,1)
        date_from = self.date_from or date_top_from
        self.date_to = self.date_to or date_today
        #locations = self.env["stock.location"].search(
        #    [("id", "child_of", [self.location_id.id])]
        #)

        locations = self.env["stock.location"].search([("id", "=", self.location_id.id)])
        self._cr.execute(
            """
            SELECT move_line.date, move_line.product_id, move_line.qty_done,
                move_line.product_uom_qty, move_line.product_uom_id, move_line.reference,
                move_line.location_id, move_line.location_dest_id,
                case when move_line.location_dest_id in %s
                    then move_line.qty_done end as product_in,
                case when move_line.location_id in %s
                    then move_line.qty_done end as product_out,
                case when move_line.date < %s then True else False end as is_initial,
                move_line.picking_id
            FROM stock_move move 
            LEFT JOIN stock_move_line move_line ON (move_line.move_id=move.id)
            WHERE (move_line.location_id in %s or move_line.location_dest_id in %s)
                and move_line.state = 'done' and move_line.product_id in %s
                and move_line.date <= %s
            ORDER BY move_line.date, move_line.reference
        """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                self.date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["stock.card.view"]
        self.results = [ReportLine.new(line).id for line in stock_card_results]

    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
            or self.env.ref("stock_card_report.action_stock_card_report_pdf")
        )
        return action.report_action(self, config=False)

    def substract_hours(self, date):
        date = date - timedelta(hours=4)
        return date
        
    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "stock_card_report.report_stock_card_report_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
