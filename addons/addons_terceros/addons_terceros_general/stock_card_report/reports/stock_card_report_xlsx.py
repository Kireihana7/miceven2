# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, _
from odoo.exceptions import UserError, Warning

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.stock_card_report.report_stock_card_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        #force language
        self = self.with_context(lang=self.env.user.lang)
        # raise UserError(_(self.env.user.lang))

        for product in objects.product_ids:
            for ws_params in self._get_ws_params(workbook, data, product):
                ws_name = ws_params.get("ws_name")
                ws_name = self._check_ws_name(ws_name)
                ws = workbook.add_worksheet(ws_name)
                generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                generate_ws_method(workbook, ws, ws_params, data, objects, product)

    def _get_ws_params(self, wb, data, product):
        language = self.env.user.lang
        
        date_from_txt = 'Date From'
        if 'es_' in language:
            date_from_txt = 'Fecha Desde'            
        # ====================================================== #
        date_to_txt = 'Date To'
        if 'es_' in language:
            date_to_txt = 'Fecha Hasta'               
        # ====================================================== #
        location_txt = 'Location'
        if 'es_' in language:
            location_txt = 'Ubicación'              
        # ====================================================== #
        initial_txt = 'Initial'
        if 'es_' in language:
            initial_txt = 'Inicial'             
        # ====================================================== #
        date_txt = 'Date'
        if 'es_' in language:
            date_txt = 'Fecha'             
        # ====================================================== #
        reference_txt = 'Reference'
        if 'es_' in language:
            reference_txt = 'Referencia'               
        # ====================================================== #
        in_txt = 'In'
        if 'es_' in language:
            in_txt = 'Entrada'            
        # ====================================================== #
        out_txt = 'Out'
        if 'es_' in language:
            out_txt = 'Salida'          
        # ====================================================== #
        balance_txt = 'Balance'
        if 'es_' in language:
            balance_txt = 'Balance'           
        # ====================================================== #

        filter_template = {
            "1_date_from": {
                "header": {"value": date_from_txt},
                "data": {
                    "value": self._render("date_from"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "2_date_to": {
                "header": {"value": date_to_txt},
                "data": {
                    "value": self._render("date_to"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "3_location": {
                "header": {"value": location_txt},
                "data": {
                    "value": self._render("location"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
        }
        initial_template = {
            "1_ref": {
                "data": {"value": initial_txt, "format": FORMATS["format_tcell_center"]},
                "colspan": 4,
            },
            "2_balance": {
                "data": {
                    "value": self._render("balance"),
                    "format": FORMATS["format_tcell_amount_right"],
                }
            },
        }
        stock_card_template = {
            "1_date": {
                "header": {"value": date_txt},
                "data": {
                    "value": self._render("date"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 25,
            },
            "2_reference": {
                "header": {"value": reference_txt},
                "data": {
                    "value": self._render("reference"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 25,
            },
            "3_input": {
                "header": {"value": in_txt},
                "data": {"value": self._render("input")},
                "width": 25,
            },
            "4_output": {
                "header": {"value": out_txt},
                "data": {"value": self._render("output")},
                "width": 25,
            },
            "5_balance": {
                "header": {"value": balance_txt},
                "data": {"value": self._render("balance")},
                "width": 25,
            },
        }

        ws_params = {
            "ws_name": product.name,
            "generate_ws_method": "_stock_card_report",
            "title": "Stock Card - {}".format(product.name),
            "wanted_list_filter": [k for k in sorted(filter_template.keys())],
            "col_specs_filter": filter_template,
            "wanted_list_initial": [k for k in sorted(initial_template.keys())],
            "col_specs_initial": initial_template,
            "wanted_list": [k for k in sorted(stock_card_template.keys())],
            "col_specs": stock_card_template,
        }
        return [ws_params]

    def _stock_card_report(self, wb, ws, ws_params, data, objects, product):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)
        # Title
        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        # Filter Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                "date_from": objects.date_from or "",
                "date_to": objects.date_to or "",
                "location": objects.location_id.display_name or "",
            },
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos += 1
        # Stock Card Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
        )
        ws.freeze_panes(row_pos, 0)
        balance = objects._get_initial(
            objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={"balance": balance},
            col_specs="col_specs_initial",
            wanted_list="wanted_list_initial",
        )
        product_lines = objects.results.filtered(
            lambda l: l.product_id == product and not l.is_initial
        )

        # UPDATE - Total Values:
        total_in = 0
        total_out = 0
        total_balance = 0

        for line in product_lines:
            balance += line.product_in - line.product_out
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={
                    "date": line.date or "",
                    "reference": line.display_name or "",
                    "input": line.product_in or 0,
                    "output": line.product_out or 0,
                    "balance": balance,
                },
                default_format=FORMATS["format_tcell_amount_right"],
            )

            total_in += line.product_in or 0
            total_out += line.product_out or 0
            total_balance += balance

        # UPDATE - Total Values:
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                "date": '',
                "reference": '',
                "input": total_in,
                "output": total_out,
                "balance": total_balance,
            },
            default_format=FORMATS["format_tcell_amount_right_bold"],
        )