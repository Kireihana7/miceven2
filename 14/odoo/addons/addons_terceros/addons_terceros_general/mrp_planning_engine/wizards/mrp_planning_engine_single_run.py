﻿# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from odoo.tools import float_compare, float_is_zero, float_round, date_utils
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

logger = logging.getLogger(__name__)


class MRPPlanningEngineSingleRun(models.TransientModel):
    _name = 'mrp.planning.engine.single.run'
    _description = 'MRP Planning Engine Single Run'

    mrp_parameter_id = fields.Many2one("mrp.parameter", "MRP Planning Parameters", required=True)


    def action_planning_engine_single_run(self):
        message = self.planning_engine_single_run(self.mrp_parameter_id)
        t_mess_id = False
        if message:
            t_mess_id = self.env["mrp.planning.message"].create({'name': message}).id
        else:
            t_mess_id = self.env["mrp.planning.message"].create({'name': 'no planning result'}).id
        return {
            'type': 'ir.actions.act_window',
            'name': _('MRP Planning Single Run Results'),
            'res_model': "mrp.planning.message",
            'res_id': t_mess_id,
            'views': [(self.env.ref('mrp_planning_engine.view_mrp_planning_message_form').id, "form")],
            'target': 'new',
        }

    def planning_engine_single_run(self, mrp_parameter_id):
        message = False
        mrp_planned_order_counter = rop_planned_order_counter = 0
        self._mrp_cleanup(mrp_parameter_id)
        self._init_mrp_element(mrp_parameter_id)
        if mrp_parameter_id.mrp_type != "R":
            mrp_planned_order_counter = self._mrp_single_calculation(mrp_parameter_id)
            if mrp_parameter_id.warehouse_id.company_id.forward_planning:
                self._forward_single_scheduling(mrp_parameter_id)
        else:
            rop_planned_order_counter = self._rop_single_calculation(mrp_parameter_id)
        planned_order_counter = mrp_planned_order_counter + rop_planned_order_counter
        message = _('planned orders: %r' %(planned_order_counter))
        return message

    def _mrp_cleanup(self, mrp_parameter_id):
        logger.info("Start MRP Cleanup")
        domain_element = [("mrp_parameter_id", "=", mrp_parameter_id.id), ("fixed", "=", False), ("mrp_origin", "not in", ("st", "mrp", "spo"))]
        self.env["mrp.element"].search(domain_element).unlink()
        demand_domain_element = [("mrp_parameter_id", "=", mrp_parameter_id.id), ("mrp_origin", "=", "di"), ("mrp_type", "=", "d")]
        self.env["mrp.element"].search(demand_domain_element).unlink()
        sales_domain_element = [("mrp_parameter_id", "=", mrp_parameter_id.id), ("mrp_origin", "=", "so"), ("mrp_type", "=", "d")]
        self.env["mrp.element"].search(sales_domain_element).unlink()
        domain_order = [("mrp_parameter_id", "=", mrp_parameter_id.id), ("fixed", "=", False)]
        self.env["mrp.planned.order"].search(domain_order).unlink()
        logger.info("End MRP Cleanup")

    def _init_mrp_element(self, mrp_parameter):
        logger.info("Start MRP initialisation")
        self._init_mrp_element_from_demand(mrp_parameter)
        self._init_mrp_element_from_stock_move(mrp_parameter)
        self._init_mrp_element_from_rfq(mrp_parameter)
        self._init_mrp_element_from_fixed_planned_order(mrp_parameter)
        logger.info("End MRP initialisation")

    def _init_mrp_element_from_demand(self, mrp_parameter):
        demand_items = self.env["mrp.demand"].search([("mrp_parameter_id", "=", mrp_parameter.id), ("state", "=", "done")])
        for demand_item in demand_items:
            demand_item_data = mrp_parameter._prepare_mrp_element_data_from_demand(demand_item)
            self.env["mrp.element"].create(demand_item_data)

    def _init_mrp_element_from_stock_move(self, mrp_parameter):
        in_domain = mrp_parameter._in_stock_moves_domain()
        in_moves = self.env["stock.move"].search(in_domain)
        if in_moves:
            for move in in_moves:
                in_move_data = mrp_parameter._prepare_data_from_stock_move(move, direction="in")
                self.env["mrp.element"].create(in_move_data)
        out_domain = mrp_parameter._out_stock_moves_domain()
        out_moves = self.env["stock.move"].search(out_domain)
        if out_moves:
            for move in out_moves:
                out_move_data = mrp_parameter._prepare_data_from_stock_move(move, direction="out")
                self.env["mrp.element"].create(out_move_data)

    def _init_mrp_element_from_rfq(self, mrp_parameter):
        location_ids = mrp_parameter.location_ids
        picking_type_ids = self.env["stock.picking.type"].search([("default_location_dest_id", "in", location_ids.ids), ("code", "=", "incoming")]).ids
        pos = self.env["purchase.order"].search([("picking_type_id", "in", picking_type_ids),("state", "in", ["draft", "sent", "to approve"])])
        po_lines = self.env["purchase.order.line"].search([("order_id", "in", pos.ids), ("product_qty", ">", 0.0),("product_id", "=", mrp_parameter.product_id.id)])
        for po_line in po_lines:
            rfq_element_data = mrp_parameter._prepare_mrp_element_data_from_rfq(po_line)
            self.env["mrp.element"].create(rfq_element_data)

    def _init_mrp_element_from_fixed_planned_order(self, mrp_parameter):
        planned_orders = self.env["mrp.planned.order"].search([
            ("mrp_parameter_id", "=", mrp_parameter.id),
            ("mrp_qty", ">", 0.0),
            ("due_date", "!=", False),
            ("relevant_planning", "=", True),
            ("fixed", "=", True)])
        for planned_order in planned_orders:
            planned_order.relevant_planning = False
            mrp_element_data = mrp_parameter._prepare_mrp_element_data_from_planned_order(planned_order)
            self.env["mrp.element"].create(mrp_element_data)

    def _mrp_single_calculation(self, mrp_parameter_id):
        logger.info("Start MRP single calculation")
        planned_order_counter = 0
        stock_mrp = 0.0
        release_date = mrp_date = False
        try:
            if not mrp_parameter_id.warehouse_id.calendar_id:
                raise UserError(_("Working Calendar not assigned to Warehouse %s.")% mrp_parameter_id.warehouse_id.name)
            stock_mrp = mrp_parameter_id._compute_qty_available()
            if stock_mrp < mrp_parameter_id.mrp_minimum_stock:
                qty_to_order = mrp_parameter_id.mrp_minimum_stock - stock_mrp
                lot_qty, number_lots = mrp_parameter_id._get_lot_qty(qty_to_order)
                if number_lots > mrp_parameter_id.company_id.number_maximum_lots:
                    raise UserError(_('please check lot quantity'))
                mrp_date = mrp_parameter_id._get_finish_date(datetime.now())
                # planned order creation
                if lot_qty > 0:
                    for i in range(number_lots):
                        planned_order = self.create_backward_planned_order(mrp_parameter_id, mrp_date, lot_qty)
                        planned_order_counter += 1
                    stock_mrp += lot_qty * number_lots
            for mrp_element_id in mrp_parameter_id.mrp_element_ids:
                qty_to_order = mrp_parameter_id.mrp_minimum_stock - stock_mrp - mrp_element_id.mrp_qty
                if qty_to_order > 0.0:
                    mrp_date = datetime.strptime(str(mrp_element_id.mrp_date), DEFAULT_SERVER_DATE_FORMAT) #from date to datetime
                    if mrp_parameter_id.lot_qty_method == 'S':
                        last_date = mrp_parameter_id.warehouse_id.calendar_id.plan_days(int(mrp_parameter.mrp_coverage_days), mrp_date, True) # datetime
                        domain_damand = [
                            ('mrp_date', '>=', mrp_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                            ('mrp_date', '<=', last_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                            ('mrp_type', '=', 'd'),
                            ]
                        demand_records = mrp_parameter_id.mrp_element_ids.filtered_domain(domain_damand)
                        demand_mrp_qty = sum(demand_records.mapped('mrp_qty'))
                        qty_to_order = mrp_parameter_id.mrp_minimum_stock - stock_mrp - demand_mrp_qty
                    lot_qty, number_lots = mrp_parameter_id._get_lot_qty(qty_to_order)
                    if number_lots > mrp_parameter_id.company_id.number_maximum_lots:
                        raise UserError(_('please check lot quantity'))
                    if mrp_parameter_id.mrp_safety_time > 0 and mrp_parameter_id.warehouse_id.calendar_id:
                        mrp_date = mrp_parameter_id.warehouse_id.calendar_id.plan_days(-mrp_parameter_id.mrp_safety_time, mrp_date, True)
                    # planned order creation
                    if lot_qty > 0:
                        for i in range(number_lots):
                            planned_order = self.create_backward_planned_order(mrp_parameter_id, mrp_date, lot_qty)
                            planned_order_counter += 1
                            # strategy 50
                            if mrp_parameter_id.demand_indicator == "50" and mrp_element_id.mrp_origin == "di":
                                planned_order.conversion_indicator = False
                            # strategy 20
                            if mrp_parameter_id.demand_indicator == "20":
                                planned_order.mto_origin = mrp_element_id.mto_origin
                                planned_order.mrp_element_down_ids.mto_origin = mrp_element_id.mto_origin
                        stock_mrp += mrp_element_id.mrp_qty + lot_qty * number_lots
                else:
                    stock_mrp += mrp_element_id.mrp_qty
        except UserError as error:
            if error:
                model_id = self.env['ir.model'].search([('model', '=', 'mrp.parameter')]).id
                activity = self.env['mail.activity'].search([('res_id', '=', mrp_parameter_id.id), ('res_model_id', '=', model_id), ('note', '=', error.args[0])])
                if not activity:
                    mrp_parameter_id.activity_schedule('mail.mail_activity_data_warning', note=error.args[0], user_id=mrp_parameter_id.user_id.id)
        logger.info("End MRP single calculation")
        return planned_order_counter

    def create_backward_planned_order(self, mrp_parameter_id, mrp_date, lot_qty):
        order_data = self._prepare_backward_planned_order_data(mrp_parameter_id, lot_qty, mrp_date)
        planned_order = self.env["mrp.planned.order"].create(order_data)
        return planned_order

    def _prepare_backward_planned_order_data(self, mrp_parameter_id, lot_qty, mrp_date):
        order_release_date = mrp_parameter_id._get_start_date(mrp_date)
        return {
            "mrp_parameter_id": mrp_parameter_id.id,
            "mrp_qty": lot_qty,
            "order_release_date": order_release_date,
            "due_date": mrp_date,
            "fixed": False,
            "forward_mode_indicator": False,
            "rescheduled_due_date": False,
        }

    def _forward_single_scheduling(self, mrp_parameter_id):
        logger.info("Start Forward Planning Phase")
        planned_orders = self.env["mrp.planned.order"].search([
            ("mrp_parameter_id", "=", mrp_parameter_id.id),
            ("order_release_date", "<", datetime.now()),
            ("fixed", "!=", True)])
        order_release_date = False
        for planned_order in planned_orders:
            planned_order.rescheduled_due_date = planned_order.due_date
            planned_order.forward_mode_indicator = True
            order_release_date = mrp_parameter_id.warehouse_id.calendar_id.plan_hours(0.0, datetime.now(), True)
            planned_order.due_date = planned_order.mrp_parameter_id._get_finish_date(order_release_date)
            planned_order.order_release_date = order_release_date
        logger.info("End Forward Planning Phase")

    def _rop_single_calculation(self, mrp_parameter_id):
        logger.info("Start ROP single calculation")
        planned_order_counter = 0
        stock_mrp = 0.0
        mrp_element_in_records = False
        mrp_element_out_ready_records = False
        mrp_element_out_all_records = False
        mrp_element_in_qty = 0.0
        mrp_element_out_ready_qty = 0.0
        mrp_element_out_all_qty = 0.0
        try:
            if not mrp_parameter_id.warehouse_id.calendar_id:
                raise UserError(_("Working Calendar not assigned to Warehouse %s.")% warehouse_id.name)
            to_date = mrp_parameter_id._get_finish_date(datetime.now()) + timedelta(days=1)
            to_date = to_date.date()
            stock_mrp = mrp_parameter_id._compute_qty_available()
            domain_mrp_element_in = [
                        ('mrp_parameter_id', '=', mrp_parameter_id.id),
                        ('mrp_type', '=', 's'),
                        ('mrp_date', '<=', to_date),
                        ]
            mrp_element_in_records = self.env["mrp.element"].search(domain_mrp_element_in)
            if mrp_element_in_records:
                mrp_element_in_qty = sum(mrp_element_in_records.mapped('mrp_qty'))
            if mrp_parameter_id.requirements_method == 'N':
                stock_mrp += mrp_element_in_qty
            elif mrp_parameter_id.requirements_method == 'C':
                domain_mrp_element_out_ready = [
                    ('mrp_parameter_id', '=', mrp_parameter_id.id),
                    ('mrp_type', '=', 'd'),
                    ('mrp_date', '<=', to_date),
                    ('state','=', 'assigned'),
                    ]
                mrp_element_out_ready_records = self.env["mrp.element"].search(domain_mrp_element_out_ready)
                if mrp_element_out_ready_records:
                    mrp_element_out_ready_qty = sum(mrp_element_out_ready_records.mapped('mrp_qty'))
                stock_mrp += mrp_element_in_qty + mrp_element_out_ready_qty
            elif mrp_parameter_id.requirements_method == 'A':
                domain_mrp_element_out_all = [
                    ('mrp_parameter_id', '=', mrp_parameter_id.id),
                    ('mrp_type', '=', 'd'),
                    ('mrp_date', '<=', to_date),
                    ]
                mrp_element_out_all_records = self.env["mrp.element"].search(domain_mrp_element_out_all)
                if mrp_element_out_all_records:
                    mrp_element_out_all_qty = sum(mrp_element_out_all_records.mapped('mrp_qty'))
                stock_mrp += mrp_element_in_qty + mrp_element_out_all_qty
            if float_compare(stock_mrp, mrp_parameter_id.mrp_threshold_stock, precision_rounding=mrp_parameter_id.product_id.uom_id.rounding) < 0:
                lot_qty, number_lots = mrp_parameter_id._get_lot_qty(mrp_parameter_id.mrp_threshold_stock - stock_mrp)
                if number_lots > mrp_parameter_id.company_id.number_maximum_lots:
                    raise UserError(_('please check lot quantity'))
                # planned order creation
                if lot_qty > 0:
                    for i in range(number_lots):
                        planned_order = self.create_forward_planned_order(mrp_parameter_id, datetime.now(), lot_qty)
                        planned_order_counter += 1
        except UserError as error:
            if error:
                model_id = self.env['ir.model'].search([('model', '=', 'mrp.parameter')]).id
                activity = self.env['mail.activity'].search([('res_id', '=', mrp_parameter_id.id), ('res_model_id', '=', model_id), ('note', '=', error.args[0])])
                if not activity:
                    mrp_parameter_id.activity_schedule('mail.mail_activity_data_warning', note=error.args[0], user_id=mrp_parameter_id.user_id.id)
        logger.info("End ROP single calculation")
        return planned_order_counter

    def create_forward_planned_order(self, mrp_parameter_id, order_release_date, lot_qty):
        order_data = self._prepare_forward_planned_order_data(mrp_parameter_id, lot_qty, order_release_date)
        planned_order = self.env["mrp.planned.order"].create(order_data)
        return planned_order

    def _prepare_forward_planned_order_data(self, mrp_parameter_id, lot_qty, order_release_date):
        calendar = mrp_parameter_id.warehouse_id.calendar_id
        if calendar:
            order_release_date = calendar.plan_hours(0.0, order_release_date, True)
        due_date = mrp_parameter_id._get_finish_date(order_release_date)
        return {
            "mrp_parameter_id": mrp_parameter_id.id,
            "mrp_qty": lot_qty,
            "order_release_date": order_release_date,
            "due_date": due_date,
            "fixed": False,
            "forward_mode_indicator": True,
            "rescheduled_due_date": False,
        }
