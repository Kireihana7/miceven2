#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

STAGEVALIDATIONERRORMESSAGE = _(u"""¡Ingrese la lista de verificación para el pago '{0}'!
No puede cambiar el estado de este pago hasta que confirme que se han realizado todos los trabajos.""")


class account_payment(models.Model):
    """
    Re-write to add check lists as a part of work flow
    """
    _inherit = "account.payment"

    @api.depends("company_id", "company_id.check_line_ids_account", "company_id.check_line_ids_account.state", "check_list_line_ids_account",
                 "state")
    def _compute_check_list_len_account(self):
        """
        Compute method for 'check_list_len', 'todo_check_ids_account', and 'checklist_progress'
        """
        for payment in self:
            total_check_points = payment.company_id.check_line_ids_account.filtered(lambda line: line.state == payment.state)
            check_list_len = len(total_check_points)
            payment.check_list_len = check_list_len
            payment.checklist_progress = check_list_len and (len(payment.check_list_line_ids_account) / check_list_len) * 100 or 0.0
            todo_check_ids_account = total_check_points - payment.check_list_line_ids_account
            payment.todo_check_ids_account = [(6, 0, todo_check_ids_account.ids)]


    check_list_line_ids_account = fields.Many2many(
        "account.check.item",
        "account_payment_account_check_item_rel_table",
        "account_payment_id",
        "caccount_check_item_id",
        string="Lista de verificación",
        help="Confirme que terminó todos los puntos. De lo contrario, no podría mover la orden de etapa",
    )
    check_list_history_ids = fields.One2many(
        "account.checklist.history",
        "account_payment_id",
        string="Historial",
    )
    check_list_len = fields.Integer(
        string= "Puntos totales",
        compute= _compute_check_list_len_account,
        store= True,
    )
    todo_check_ids_account = fields.Many2many(
        "account.check.item",
        "account_payment_account_check_item_rel_table_todo",
        "account_payment_id_todo",
        "caccount_check_item_id_todo",
        string="Verificaciones por hacer",
        compute=_compute_check_list_len_account,
        store=True,
    )
    checklist_progress = fields.Float(
        string="Progreso",
        compute=_compute_check_list_len_account,
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
        payment_id = super(account_payment, self).create(vals)
        if vals.get("check_list_line_ids_account"):
            changed_items = self.env["account.check.item"].browse(vals.get("check_list_line_ids_account")[0][2])
            changed_items._check_cheklist_rights()
            payment_id._register_history(changed_items)
        return payment_id

    def write(self, vals):
        """
        Overwrite to check:
         1. if check item is entered: whether a user has rights for that
         2. if stage is changed: whether a check list is filled (in case of progress)
         3. we made the special check if a portal user "writes" state (although should not happen since portal users
            do not have rights to write in payments and there are no account entries there). To avoid serious CRITICAL\
            client misunderstandings check lists are not checked in that case and pre-entered

        Methods:
         * _check_cheklist_rights of check.item
         * _register_history
         * _check_checklist_complete
         * _recover_filled_checklist
        """
        # 1
        if vals.get("check_list_line_ids_account") and not self.env.context.get("automatic_checks"):
            new_check_line_ids_account = self.env["account.check.item"].browse(vals.get("check_list_line_ids_account")[0][2])
            for payment in self:
                old_check_line_ids_account = payment.check_list_line_ids_account
                to_add_items = (new_check_line_ids_account - old_check_line_ids_account)
                to_remove_items = (old_check_line_ids_account - new_check_line_ids_account)
                changed_items = to_add_items | to_remove_items
                changed_items._check_cheklist_rights()
                payment._register_history(to_add_items, "done")
                payment._register_history(to_remove_items, "reset")
        # 2
        if vals.get("state"):
            if not self.env.user.has_group("base.group_portal"):
                self._check_checklist_complete(vals)
                self._recover_filled_checklist(vals.get("state"))
            else:
                # 3
                self.sudo()._recover_filled_checklist(vals.get("state"))

        return super(account_payment, self).write(vals)

    def _register_history(self, changed_items, done_action="done"):
        """
        The method to register check list history by payment

        Args:
         * changed_items - dict of filled in or reset items
         * done_action - either 'done', or 'reset'
        """
        for payment in self:
            for item in changed_items:
                history_item_vals = {
                    "account_payment_id": payment.id,
                    "check_list_id": item.id,
                    "done_action": done_action,
                }
                self.env["account.checklist.history"].create(history_item_vals)

    def _check_checklist_complete(self, vals):
        """
        The method to make sure checklist is filled in case of payment progress

        Args:
         * vals - dict of of written values
        """
        for payment in self:
            company_id = self.env["res.company"].browse(vals.get("company_id") or payment.company_id.id)
            no_needed_states = company_id.no_stages_ids_account.mapped("state")
            if vals.get("state") not in no_needed_states:
                entered_len = vals.get("check_list_line_ids_account") and len(vals.get("check_list_line_ids_account")) or \
                              len(payment.check_list_line_ids_account)
                required_len = vals.get("check_list_len") and vals.get("check_list_len") or payment.check_list_len
                if entered_len != required_len:
                    raise ValidationError(STAGEVALIDATIONERRORMESSAGE.format(payment.name))

    def _recover_filled_checklist(self, state):
        """
        The method to recover already done check list from history

        Args:
         * state - char - new account payment state
        """
        for payment in self:
            to_recover = []
            already_considered = []
            for history_item in payment.check_list_history_ids:
                check_item_id = history_item.check_list_id
                if check_item_id.state == state \
                        and check_item_id.should_be_reset \
                        and check_item_id.id not in already_considered \
                        and history_item.done_action == "done":
                    to_recover.append(check_item_id.id)
                already_considered.append(check_item_id.id)
            payment.with_context(automatic_checks=True).check_list_line_ids_account = [(6, 0, to_recover)]
