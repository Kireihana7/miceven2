# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError

from odoo import api, fields, models, _
from odoo.osv import expression

TIMESHEET_INVOICE_TYPES = [
    ('billable_time', 'Billed on Timesheets'),
    ('billable_fixed', 'Billed at a Fixed price'),
    ('billable_milestones', 'Billed on Milestones'),
    ('billable_manual', 'Billed Manually'),
    ('non_billable', 'Non Billable Tasks'),
    ('timesheet_revenues', 'Timesheet Revenues'),
    ('service_revenues', 'Service Revenues'),
    ('other_revenues', 'Materials'),
    ('other_costs', 'Materials'),
]

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _default_sale_line_domain(self):
        domain = super(AccountAnalyticLine, self)._default_sale_line_domain()
        return expression.OR([domain, [('qty_delivered_method', '=', 'timesheet')]])

    timesheet_invoice_type = fields.Selection(TIMESHEET_INVOICE_TYPES, string="Billable Type",
            compute='_compute_timesheet_invoice_type', compute_sudo=True, store=True, readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', compute="_compute_commercial_partner")
    timesheet_invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, copy=False, help="Invoice created from the timesheet")
<<<<<<< HEAD
    so_line = fields.Many2one(compute="_compute_so_line", store=True, readonly=False,
        domain="[('is_service', '=', True), ('is_expense', '=', False), ('state', 'in', ['sale', 'done']), ('order_partner_id', 'child_of', commercial_partner_id)]",
        help="Sales order item to which the time spent will be added in order to be invoiced to your customer. Remove the sales order item for the timesheet entry to be non-billable.")
    # we needed to store it only in order to be able to groupby in the portal
    order_id = fields.Many2one(related='so_line.order_id', store=True, readonly=True, index=True)
    is_so_line_edited = fields.Boolean("Is Sales Order Item Manually Edited")

    @api.depends('project_id.commercial_partner_id', 'task_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for timesheet in self:
            timesheet.commercial_partner_id = timesheet.task_id.commercial_partner_id or timesheet.project_id.commercial_partner_id

    @api.depends('so_line.product_id', 'project_id', 'amount')
    def _compute_timesheet_invoice_type(self):
        for timesheet in self:
=======
    non_allow_billable = fields.Boolean("Non-Billable", help="Your timesheet will not be billed.")
    so_line = fields.Many2one(compute="_compute_so_line", store=True, readonly=False)

    # TODO: [XBO] Since the task_id is not required in this model,  then it should more efficient to depends to bill_type and pricing_type of project (See in master)
    @api.depends('so_line.product_id', 'project_id', 'task_id', 'non_allow_billable', 'task_id.bill_type', 'task_id.pricing_type', 'task_id.non_allow_billable')
    def _compute_timesheet_invoice_type(self):
        non_allowed_billable = self.filtered('non_allow_billable')
        non_allowed_billable.timesheet_invoice_type = 'non_billable_timesheet'
        non_allowed_billable_task = (self - non_allowed_billable).filtered(lambda t: t.task_id.bill_type == 'customer_project' and t.task_id.pricing_type == 'employee_rate' and t.task_id.non_allow_billable)
        non_allowed_billable_task.timesheet_invoice_type = 'non_billable'

        for timesheet in self - non_allowed_billable - non_allowed_billable_task:
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            if timesheet.project_id:  # AAL will be set to False
                invoice_type = 'non_billable' if not timesheet.so_line else False
                if timesheet.so_line and timesheet.so_line.product_id.type == 'service':
                    if timesheet.so_line.product_id.invoice_policy == 'delivery':
                        if timesheet.so_line.product_id.service_type == 'timesheet':
                            invoice_type = 'timesheet_revenues' if timesheet.amount > 0 else 'billable_time'
                        else:
                            service_type = timesheet.so_line.product_id.service_type
                            invoice_type = f'billable_{service_type}' if service_type in ['milestones', 'manual'] else 'billable_fixed'
                    elif timesheet.so_line.product_id.invoice_policy == 'order':
                        invoice_type = 'billable_fixed'
                timesheet.timesheet_invoice_type = invoice_type
            else:
                if timesheet.amount >= 0:
                    if timesheet.so_line and timesheet.so_line.product_id.type == 'service':
                        timesheet.timesheet_invoice_type = 'service_revenues'
                    else:
                        timesheet.timesheet_invoice_type = 'other_revenues'
                else:
                    timesheet.timesheet_invoice_type = 'other_costs'

    @api.depends('task_id.sale_line_id', 'project_id.sale_line_id', 'employee_id', 'project_id.allow_billable')
    def _compute_so_line(self):
        for timesheet in self.filtered(lambda t: not t.is_so_line_edited and t._is_not_billed()):  # Get only the timesheets are not yet invoiced
            timesheet.so_line = timesheet.project_id.allow_billable and timesheet._timesheet_determine_sale_line()

<<<<<<< HEAD
    @api.depends('timesheet_invoice_id.state')
    def _compute_partner_id(self):
        super(AccountAnalyticLine, self.filtered(lambda t: t._is_not_billed()))._compute_partner_id()

    @api.depends('timesheet_invoice_id.state')
    def _compute_project_id(self):
        super(AccountAnalyticLine, self.filtered(lambda t: t._is_not_billed()))._compute_project_id()

    def _is_not_billed(self):
        self.ensure_one()
        return not self.timesheet_invoice_id or self.timesheet_invoice_id.state == 'cancel'

    def _check_timesheet_can_be_billed(self):
        return self.so_line in self.project_id.mapped('sale_line_employee_ids.sale_line_id') | self.task_id.sale_line_id | self.project_id.sale_line_id
=======
    @api.depends('task_id.sale_line_id', 'project_id.sale_line_id', 'employee_id', 'project_id.allow_billable')
    def _compute_so_line(self):
        for timesheet in self._get_not_billed():  # Get only the timesheets are not yet invoiced
            timesheet.so_line = timesheet.project_id.allow_billable and timesheet._timesheet_determine_sale_line(timesheet.task_id, timesheet.employee_id, timesheet.project_id)
    
    @api.depends('timesheet_invoice_id.state')
    def _compute_partner_id(self):
        super(AccountAnalyticLine, self._get_not_billed())._compute_partner_id()

    def _get_not_billed(self):
        return self.filtered(lambda t: not t.timesheet_invoice_id or t.timesheet_invoice_id.state == 'cancel')

    def _check_timesheet_can_be_billed(self):
        return self.so_line in self.project_id.mapped('sale_line_employee_ids.sale_line_id') | self.task_id.sale_line_id | self.project_id.sale_line_id

    @api.constrains('so_line', 'project_id')
    def _check_sale_line_in_project_map(self):
        if not all(t._check_timesheet_can_be_billed() for t in self._get_not_billed().filtered(lambda t: t.project_id and t.so_line)):
            raise ValidationError(_("This timesheet line cannot be billed: there is no Sale Order Item defined on the task, nor on the project. Please define one to save your timesheet line."))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def write(self, values):
        # prevent to update invoiced timesheets if one line is of type delivery
        self._check_can_write(values)
        result = super(AccountAnalyticLine, self).write(values)
        return result

    def _check_can_write(self, values):
        if self.sudo().filtered(lambda aal: aal.so_line.product_id.invoice_policy == "delivery") and self.filtered(lambda t: t.timesheet_invoice_id and t.timesheet_invoice_id.state != 'cancel'):
            if any(field_name in values for field_name in ['unit_amount', 'employee_id', 'project_id', 'task_id', 'so_line', 'amount', 'date']):
                raise UserError(_('You cannot modify timesheets that are already invoiced.'))

<<<<<<< HEAD
    def _timesheet_determine_sale_line(self):
=======
    @api.model
    def _timesheet_preprocess(self, values):
        if values.get('task_id') and not values.get('account_id'):
            task = self.env['project.task'].browse(values.get('task_id'))
            if task.analytic_account_id:
                values['account_id'] = task.analytic_account_id.id
                values['company_id'] = task.analytic_account_id.company_id.id or task.company_id.id
        values = super(AccountAnalyticLine, self)._timesheet_preprocess(values)
        return values

    @api.model
    def _timesheet_determine_sale_line(self, task, employee, project):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        """ Deduce the SO line associated to the timesheet line:
            1/ timesheet on task rate: the so line will be the one from the task
            2/ timesheet on employee rate task: find the SO line in the map of the project (even for subtask), or fallback on the SO line of the task, or fallback
                on the one on the project
        """
<<<<<<< HEAD
        self.ensure_one()

        if not self.task_id:
            if self.project_id.pricing_type == 'employee_rate':
                map_entry = self._get_employee_mapping_entry()
                if map_entry:
                    return map_entry.sale_line_id
            if self.project_id.sale_line_id:
                return self.project_id.sale_line_id
        if self.task_id.allow_billable and self.task_id.sale_line_id:
            if self.task_id.pricing_type in ('task_rate', 'fixed_rate'):
                return self.task_id.sale_line_id
            else:  # then pricing_type = 'employee_rate'
                map_entry = self.project_id.sale_line_employee_ids.filtered(
                    lambda map_entry:
                        map_entry.employee_id == self.employee_id
                        and map_entry.sale_line_id.order_partner_id.commercial_partner_id == self.task_id.commercial_partner_id
                )
                if map_entry:
                    return map_entry.sale_line_id
                return self.task_id.sale_line_id
        return False
=======
        if not task:
            if project.bill_type == 'customer_project' and project.pricing_type == 'employee_rate':
                map_entry = self.env['project.sale.line.employee.map'].search([('project_id', '=', project.id), ('employee_id', '=', employee.id)])
                if map_entry:
                    return map_entry.sale_line_id
            if project.sale_line_id:
                return project.sale_line_id
        if task.allow_billable and task.sale_line_id:
            if task.bill_type == 'customer_task':
                return task.sale_line_id
            if task.pricing_type == 'fixed_rate':
                return task.sale_line_id
            elif task.pricing_type == 'employee_rate' and not task.non_allow_billable:
                map_entry = project.sale_line_employee_ids.filtered(lambda map_entry: map_entry.employee_id == employee)
                if map_entry:
                    return map_entry.sale_line_id
                if task.sale_line_id or project.sale_line_id:
                    return task.sale_line_id or project.sale_line_id
        return self.env['sale.order.line']
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def _timesheet_get_portal_domain(self):
        """ Only the timesheets with a product invoiced on delivered quantity are concerned.
            since in ordered quantity, the timesheet quantity is not invoiced,
            thus there is no meaning of showing invoice with ordered quantity.
        """
        domain = super(AccountAnalyticLine, self)._timesheet_get_portal_domain()
        return expression.AND([domain, [('timesheet_invoice_type', 'in', ['billable_time', 'non_billable', 'billable_fixed'])]])

    @api.model
    def _timesheet_get_sale_domain(self, order_lines_ids, invoice_ids):
        if not invoice_ids:
            return [('so_line', 'in', order_lines_ids.ids)]

        return [
            '|',
            '&',
            ('timesheet_invoice_id', 'in', invoice_ids.ids),
            # TODO : Master: Check if non_billable should be removed ?
            ('timesheet_invoice_type', 'in', ['billable_time', 'non_billable']),
            '&',
            ('timesheet_invoice_type', '=', 'billable_fixed'),
            ('so_line', 'in', order_lines_ids.ids)
        ]

    def _get_timesheets_to_merge(self):
        res = super(AccountAnalyticLine, self)._get_timesheets_to_merge()
        return res.filtered(lambda l: not l.timesheet_invoice_id or l.timesheet_invoice_id.state != 'posted')

    @api.ondelete(at_uninstall=False)
    def _unlink_except_invoiced(self):
        if any(line.timesheet_invoice_id and line.timesheet_invoice_id.state == 'posted' for line in self):
            raise UserError(_('You cannot remove a timesheet that has already been invoiced.'))

    def _get_employee_mapping_entry(self):
        self.ensure_one()
        return self.env['project.sale.line.employee.map'].search([('project_id', '=', self.project_id.id), ('employee_id', '=', self.employee_id.id or self.env.user.employee_id.id)])

    def _hourly_cost(self):
        if self.project_id.pricing_type == 'employee_rate':
            mapping_entry = self._get_employee_mapping_entry()
            if mapping_entry:
                return mapping_entry.cost
        return super()._hourly_cost()
