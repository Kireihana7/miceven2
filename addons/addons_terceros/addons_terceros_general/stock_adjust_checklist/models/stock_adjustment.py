#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

STAGEVALIDATIONERRORMESSAGE = _(u"""¡Ingrese la lista de verificación para la orden de venta '{0}'!
No puede cambiar el estado de este pedido de venta hasta que confirme que se han realizado todos los trabajos.""")


class stock_order(models.Model):
    """
    Re-write to add check lists as a part of work flow
    """
    _inherit = "stock.inventory"

    @api.depends("company_id", "company_id.check_line_ids_stock", "company_id.check_line_ids_stock.state", "check_list_line_ids_stock",
                 "state")
    def _compute_check_list_len_stock(self):
        """
        Compute method for 'check_list_len', 'todo_check_ids_stock', and 'checklist_progress'
        """
        for order in self:
            total_check_points = order.company_id.check_line_ids_stock.filtered(lambda line: line.state == order.state)
            check_list_len = len(total_check_points)
            order.check_list_len = check_list_len
            order.checklist_progress = check_list_len and (len(order.check_list_line_ids_stock) / check_list_len) * 100 or 0.0
            todo_check_ids_stock = total_check_points - order.check_list_line_ids_stock
            order.todo_check_ids_stock = [(6, 0, todo_check_ids_stock.ids)]


    check_list_line_ids_stock = fields.Many2many(
        "stock.check.item",
        "stock_order_stock_check_item_rel_table",
        "stock_order_id",
        "cstock_check_item_id",
        string="Lista de verificación",
        help="Confirme que terminó todos los puntos. De lo contrario, no podría mover la orden de etapa",
    )
    check_list_history_ids = fields.One2many(
        "stock.checklist.history",
        "stock_order_id",
        string="Historial",
    )
    check_list_len = fields.Integer(
        string= "Puntos totales",
        compute= _compute_check_list_len_stock,
        store= True,
    )
    todo_check_ids_stock = fields.Many2many(
        "stock.check.item",
        "stock_order_stock_check_item_rel_table_todo",
        "stock_order_id_todo",
        "cstock_check_item_id_todo",
        string="Verificaciones por hacer",
        compute=_compute_check_list_len_stock,
        store=True,
    )
    checklist_progress = fields.Float(
        string="Progreso",
        compute=_compute_check_list_len_stock,
        store=True,
    )

    @api.model
    def create(self, vals):
        """
        Overwrite to check whether the check list is pre-filled and check whether this user might do that

        Methods:
         * _check_cheklist_rights of check.item
         * _register_history
        """
        order_id = super(stock_order, self).create(vals)
        if vals.get("check_list_line_ids_stock"):
            changed_items = self.env["stock.check.item"].browse(vals.get("check_list_line_ids_stock")[0][2])
            changed_items._check_cheklist_rights()
            order_id._register_history(changed_items)
        return order_id

    def write(self, vals):
        """
        Overwrite to check:
         1. if check item is entered: whether a user has rights for that
         2. if stage is changed: whether a check list is filled (in case of progress)
         3. we made the special check if a portal user "writes" state (although should not happen since portal users
            do not have rights to write in orders and there are no stock entries there). To avoid serious CRITICAL\
            client misunderstandings check lists are not checked in that case and pre-entered

        Methods:
         * _check_cheklist_rights of check.item
         * _register_history
         * _check_checklist_complete
         * _recover_filled_checklist
        """
        # 1
        if vals.get("check_list_line_ids_stock") and not self.env.context.get("automatic_checks"):
            new_check_line_ids_stock = self.env["stock.check.item"].browse(vals.get("check_list_line_ids_stock")[0][2])
            for order in self:
                old_check_line_ids_stock = order.check_list_line_ids_stock
                to_add_items = (new_check_line_ids_stock - old_check_line_ids_stock)
                to_remove_items = (old_check_line_ids_stock - new_check_line_ids_stock)
                changed_items = to_add_items | to_remove_items
                changed_items._check_cheklist_rights()
                order._register_history(to_add_items, "done")
                order._register_history(to_remove_items, "reset")
        # 2
        if vals.get("state"):
            if not self.env.user.has_group("base.group_portal"):
                self._check_checklist_complete(vals)
                self._recover_filled_checklist(vals.get("state"))
            else:
                # 3
                self.sudo()._recover_filled_checklist(vals.get("state"))

        return super(stock_order, self).write(vals)

    def _register_history(self, changed_items, done_action="done"):
        """
        The method to register check list history by order

        Args:
         * changed_items - dict of filled in or reset items
         * done_action - either 'done', or 'reset'
        """
        for order in self:
            for item in changed_items:
                history_item_vals = {
                    "stock_order_id": order.id,
                    "check_list_id": item.id,
                    "done_action": done_action,
                }
                self.env["stock.checklist.history"].create(history_item_vals)

    def _check_checklist_complete(self, vals):
        """
        The method to make sure checklist is filled in case of order progress

        Args:
         * vals - dict of of written values
        """
        for order in self:
            company_id = self.env["res.company"].browse(vals.get("company_id") or order.company_id.id)
            no_needed_states = company_id.no_stages_ids_stock.mapped("state")
            if vals.get("state") not in no_needed_states:
                entered_len = vals.get("check_list_line_ids_stock") and len(vals.get("check_list_line_ids_stock")) or \
                              len(order.check_list_line_ids_stock)
                required_len = vals.get("check_list_len") and vals.get("check_list_len") or order.check_list_len
                if entered_len != required_len:
                    raise ValidationError(STAGEVALIDATIONERRORMESSAGE.format(order.name))

    def _recover_filled_checklist(self, state):
        """
        The method to recover already done check list from history

        Args:
         * state - char - new stock order state
        """
        for order in self:
            to_recover = []
            already_considered = []
            for history_item in order.check_list_history_ids:
                check_item_id = history_item.check_list_id
                if check_item_id.state == state \
                        and check_item_id.should_be_reset \
                        and check_item_id.id not in already_considered \
                        and history_item.done_action == "done":
                    to_recover.append(check_item_id.id)
                already_considered.append(check_item_id.id)
            order.with_context(automatic_checks=True).check_list_line_ids_stock = [(6, 0, to_recover)]
