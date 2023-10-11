# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, tools, _
from odoo.tools import float_compare, float_is_zero
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
import re
from math import copysign
from collections import defaultdict
from dateutil.relativedelta import relativedelta


class AccountReconcileModelPartnerMapping(models.Model):
    _name = 'account.reconcile.model.partner.mapping'
    _description = 'Partner mapping for reconciliation models'

    model_id = fields.Many2one(comodel_name='account.reconcile.model', readonly=True, required=True, ondelete='cascade')
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner", required=True, ondelete='cascade')
    payment_ref_regex = fields.Char(string="Find Text in Label")
    narration_regex = fields.Char(string="Find Text in Notes")

    @api.constrains('narration_regex', 'payment_ref_regex')
    def validate_regex(self):
        for record in self:
            if not (record.narration_regex or record.payment_ref_regex):
                raise ValidationError(_("Please set at least one of the match texts to create a partner mapping."))
            try:
                if record.payment_ref_regex:
                    current_regex = record.payment_ref_regex
                    re.compile(record.payment_ref_regex)
                if record.narration_regex:
                    current_regex = record.narration_regex
                    re.compile(record.narration_regex)
            except re.error:
                raise ValidationError(_("The following regular expression is invalid to create a partner mapping: %s") % current_regex)
<<<<<<< HEAD

=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

class AccountReconcileModelLine(models.Model):
    _name = 'account.reconcile.model.line'
    _inherit = 'analytic.mixin'
    _description = 'Rules for the reconciliation model'
    _order = 'sequence, id'
    _check_company_auto = True

    model_id = fields.Many2one('account.reconcile.model', readonly=True, ondelete='cascade')
<<<<<<< HEAD
    allow_payment_tolerance = fields.Boolean(related='model_id.allow_payment_tolerance')
    payment_tolerance_param = fields.Float(related='model_id.payment_tolerance_param')
=======
    match_total_amount = fields.Boolean(related='model_id.match_total_amount')
    match_total_amount_param = fields.Float(related='model_id.match_total_amount_param')
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    rule_type = fields.Selection(related='model_id.rule_type')
    company_id = fields.Many2one(related='model_id.company_id', store=True)
    sequence = fields.Integer(required=True, default=10)
    account_id = fields.Many2one('account.account', string='Account', ondelete='cascade',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('is_off_balance', '=', False)]",
        required=True, check_company=True)

    # This field is ignored in a bank statement reconciliation.
    journal_id = fields.Many2one('account.journal', string='Journal', ondelete='cascade',
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]", check_company=True)
    label = fields.Char(string='Journal Item Label')
    amount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage of balance'),
        ('percentage_st_line', 'Percentage of statement line'),
        ('regex', 'From label'),
    ], required=True, default='percentage')

    # used to show the force tax included button'
    show_force_tax_included = fields.Boolean(compute='_compute_show_force_tax_included')
    force_tax_included = fields.Boolean(string='Tax Included in Price', help='Force the tax to be managed as a price included tax.')
    # technical shortcut to parse the amount to a float
    amount = fields.Float(string="Float Amount", compute='_compute_float_amount', store=True)
    amount_string = fields.Char(string="Amount", default='100', required=True, help="""Value for the amount of the writeoff line
    * Percentage: Percentage of the balance, between 0 and 100.
    * Fixed: The fixed value of the writeoff. The amount will count as a debit if it is negative, as a credit if it is positive.
    * From Label: There is no need for regex delimiter, only the regex is needed. For instance if you want to extract the amount from\nR:9672938 10/07 AX 9415126318 T:5L:NA BRT: 3358,07 C:\nYou could enter\nBRT: ([\d,]+)""")
    tax_ids = fields.Many2many('account.tax', string='Taxes', ondelete='restrict', check_company=True)

    @api.onchange('tax_ids')
    def _onchange_tax_ids(self):
        # Multiple taxes with force_tax_included results in wrong computation, so we
        # only allow to set the force_tax_included field if we have one tax selected
        if len(self.tax_ids) != 1:
            self.force_tax_included = False

    @api.depends('tax_ids')
    def _compute_show_force_tax_included(self):
        for record in self:
            record.show_force_tax_included = False if len(record.tax_ids) != 1 else True

    @api.onchange('amount_type')
    def _onchange_amount_type(self):
        self.amount_string = ''
        if self.amount_type in ('percentage', 'percentage_st_line'):
            self.amount_string = '100'
        elif self.amount_type == 'regex':
            self.amount_string = '([\d,]+)'

    @api.depends('amount_string')
    def _compute_float_amount(self):
        for record in self:
            try:
                record.amount = float(record.amount_string)
            except ValueError:
                record.amount = 0

    @api.constrains('amount_string')
    def _validate_amount(self):
        for record in self:
            if record.amount_type == 'fixed' and record.amount == 0:
<<<<<<< HEAD
                raise UserError(_("The amount is not a number"))
            if record.amount_type == 'percentage_st_line' and record.amount == 0:
                raise UserError(_("Balance percentage can't be 0"))
            if record.amount_type == 'percentage' and record.amount == 0:
                raise UserError(_("Statement line percentage can't be 0"))
=======
                raise UserError(_('The amount is not a number'))
            if record.amount_type == 'percentage' and not 0 < record.amount:
                raise UserError(_('The amount is not a percentage'))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            if record.amount_type == 'regex':
                try:
                    re.compile(record.amount_string)
                except re.error:
                    raise UserError(_('The regex is not valid'))

    def _prepare_aml_vals(self, partner):
        """ Prepare a dictionary that will be used later to create a new journal item (account.move.line) for the
        given reconcile model line.

        :param partner: The partner to be linked to the journal item.
        :return:        A python dictionary.
        """
        self.ensure_one()

        taxes = self.tax_ids
        if taxes and partner:
            fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(partner)
            if fiscal_position:
                taxes = fiscal_position.map_tax(taxes)

        return {
            'name': self.label,
            'account_id': self.account_id.id,
            'partner_id': partner.id,
            'analytic_distribution': self.analytic_distribution,
            'tax_ids': [Command.set(taxes.ids)],
            'reconcile_model_id': self.model_id.id,
        }

    def _apply_in_manual_widget(self, residual_amount_currency, partner, currency):
        """ Prepare a dictionary that will be used later to create a new journal item (account.move.line) for the
        given reconcile model line used by the manual reconciliation widget.

        Note: 'journal_id' is added to the returned dictionary even if it is a related readonly field.
        It's a hack for the manual reconciliation widget. Indeed, a single journal entry will be created for each
        journal.

        :param residual_amount_currency:    The current balance expressed in the account's currency.
        :param partner:                     The partner to be linked to the journal item.
        :param currency:                    The currency set on the account in the manual reconciliation widget.
        :return:                            A python dictionary.
        """
        self.ensure_one()

        if self.amount_type == 'percentage':
            amount_currency = currency.round(residual_amount_currency * (self.amount / 100.0))
        elif self.amount_type == 'fixed':
            sign = 1 if residual_amount_currency > 0.0 else -1
            amount_currency = currency.round(self.amount * sign)
        else:
            raise UserError(_("This reconciliation model can't be used in the manual reconciliation widget because its "
                              "configuration is not adapted"))

        return {
            **self._prepare_aml_vals(partner),
            'currency_id': currency.id,
            'amount_currency': amount_currency,
            'journal_id': self.journal_id.id,
        }

    def _apply_in_bank_widget(self, residual_amount_currency, partner, st_line):
        """ Prepare a dictionary that will be used later to create a new journal item (account.move.line) for the
        given reconcile model line used by the bank reconciliation widget.

        :param residual_amount_currency:    The current balance expressed in the statement line's currency.
        :param partner:                     The partner to be linked to the journal item.
        :param st_line:                     The statement line mounted inside the bank reconciliation widget.
        :return:                            A python dictionary.
        """
        self.ensure_one()
        currency = st_line.foreign_currency_id or st_line.journal_id.currency_id or st_line.company_currency_id

        amount_currency = None
        if self.amount_type == 'percentage_st_line':
            amount_currency = currency.round(residual_amount_currency * (self.amount / 100.0))
        elif self.amount_type == 'regex':
            match = re.search(self.amount_string, st_line.payment_ref)
            if match:
                sign = 1 if residual_amount_currency > 0.0 else -1
                decimal_separator = self.model_id.decimal_separator
                try:
                    extracted_match_group = re.sub(r'[^\d' + decimal_separator + ']', '', match.group(1))
                    extracted_balance = float(extracted_match_group.replace(decimal_separator, '.'))
                    amount_currency = copysign(extracted_balance * sign, residual_amount_currency)
                except ValueError:
                    amount_currency = 0.0
            else:
                amount_currency = 0.0

        if amount_currency is None:
            aml_vals = self._apply_in_manual_widget(residual_amount_currency, partner, currency)
        else:
            aml_vals = {
                **self._prepare_aml_vals(partner),
                'currency_id': currency.id,
                'amount_currency': amount_currency,
            }

        if not aml_vals['name']:
            aml_vals['name'] = st_line.payment_ref

        return aml_vals


class AccountReconcileModel(models.Model):
    _name = 'account.reconcile.model'
    _description = 'Preset to create journal entries during a invoices and payments matching'
    _inherit = ['mail.thread']
    _order = 'sequence, id'
    _check_company_auto = True

    _sql_constraints = [('name_unique', 'unique(name, company_id)', 'A reconciliation model already bears this name.')]

    # Base fields.
    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    rule_type = fields.Selection(selection=[
<<<<<<< HEAD
        ('writeoff_button', 'Button to generate counterpart entry'),
        ('writeoff_suggestion', 'Rule to suggest counterpart entry'),
        ('invoice_matching', 'Rule to match invoices/bills'),
    ], string='Type', default='writeoff_button', required=True, tracking=True)
    auto_reconcile = fields.Boolean(string='Auto-validate', tracking=True,
=======
        ('writeoff_button', 'Manually create a write-off on clicked button'),
        ('writeoff_suggestion', 'Suggest counterpart values'),
        ('invoice_matching', 'Match existing invoices/bills'),
    ], string='Type', default='writeoff_button', required=True)
    auto_reconcile = fields.Boolean(string='Auto-validate',
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        help='Validate the statement line automatically (reconciliation based on your rule).')
    to_check = fields.Boolean(string='To Check', default=False, help='This matching rule is used when the user is not certain of all the information of the counterpart.')
    matching_order = fields.Selection(
        selection=[
            ('old_first', 'Oldest first'),
            ('new_first', 'Newest first'),
        ],
        required=True,
        default='old_first',
        tracking=True,
    )

    # ===== Conditions =====
    match_text_location_label = fields.Boolean(
        default=True,
        help="Search in the Statement's Label to find the Invoice/Payment's reference",
        tracking=True,
    )
    match_text_location_note = fields.Boolean(
        default=False,
        help="Search in the Statement's Note to find the Invoice/Payment's reference",
        tracking=True,
    )
    match_text_location_reference = fields.Boolean(
        default=False,
        help="Search in the Statement's Reference to find the Invoice/Payment's reference",
        tracking=True,
    )
    match_journal_ids = fields.Many2many('account.journal', string='Journals Availability',
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        check_company=True,
        help='The reconciliation model will only be available from the selected journals.')
    match_nature = fields.Selection(selection=[
        ('amount_received', 'Received'),
        ('amount_paid', 'Paid'),
        ('both', 'Paid/Received')
    ], string='Amount Type', required=True, default='both', tracking=True,
        help='''The reconciliation model will only be applied to the selected transaction type:
        * Amount Received: Only applied when receiving an amount.
        * Amount Paid: Only applied when paying an amount.
        * Amount Paid/Received: Applied in both cases.''')
    match_amount = fields.Selection(selection=[
        ('lower', 'Is Lower Than'),
        ('greater', 'Is Greater Than'),
        ('between', 'Is Between'),
    ], string='Amount Condition', tracking=True,
        help='The reconciliation model will only be applied when the amount being lower than, greater than or between specified amount(s).')
    match_amount_min = fields.Float(string='Amount Min Parameter', tracking=True)
    match_amount_max = fields.Float(string='Amount Max Parameter', tracking=True)
    match_label = fields.Selection(selection=[
        ('contains', 'Contains'),
        ('not_contains', 'Not Contains'),
        ('match_regex', 'Match Regex'),
    ], string='Label', tracking=True, help='''The reconciliation model will only be applied when the label:
        * Contains: The proposition label must contains this string (case insensitive).
        * Not Contains: Negation of "Contains".
        * Match Regex: Define your own regular expression.''')
    match_label_param = fields.Char(string='Label Parameter', tracking=True)
    match_note = fields.Selection(selection=[
        ('contains', 'Contains'),
        ('not_contains', 'Not Contains'),
        ('match_regex', 'Match Regex'),
    ], string='Note', tracking=True, help='''The reconciliation model will only be applied when the note:
        * Contains: The proposition note must contains this string (case insensitive).
        * Not Contains: Negation of "Contains".
        * Match Regex: Define your own regular expression.''')
    match_note_param = fields.Char(string='Note Parameter', tracking=True)
    match_transaction_type = fields.Selection(selection=[
        ('contains', 'Contains'),
        ('not_contains', 'Not Contains'),
        ('match_regex', 'Match Regex'),
    ], string='Transaction Type', tracking=True, help='''The reconciliation model will only be applied when the transaction type:
        * Contains: The proposition transaction type must contains this string (case insensitive).
        * Not Contains: Negation of "Contains".
        * Match Regex: Define your own regular expression.''')
    match_transaction_type_param = fields.Char(string='Transaction Type Parameter', tracking=True)
    match_same_currency = fields.Boolean(string='Same Currency', default=True, tracking=True,
        help='Restrict to propositions having the same currency as the statement line.')
    allow_payment_tolerance = fields.Boolean(
        string="Payment Tolerance",
        default=True,
        tracking=True,
        help="Difference accepted in case of underpayment.",
    )
    payment_tolerance_param = fields.Float(
        string="Gap",
        compute='_compute_payment_tolerance_param',
        readonly=False,
        store=True,
        tracking=True,
        help="The sum of total residual amount propositions matches the statement line amount under this amount/percentage.",
    )
    payment_tolerance_type = fields.Selection(
        selection=[('percentage', "in percentage"), ('fixed_amount', "in amount")],
        default='percentage',
        required=True,
        tracking=True,
        help="The sum of total residual amount propositions and the statement line amount allowed gap type.",
    )
    match_partner = fields.Boolean(string='Partner is Set', tracking=True,
        help='The reconciliation model will only be applied when a customer/vendor is set.')
    match_partner_ids = fields.Many2many('res.partner', string='Matching partners',
        help='The reconciliation model will only be applied to the selected customers/vendors.')
    match_partner_category_ids = fields.Many2many('res.partner.category', string='Matching categories',
        help='The reconciliation model will only be applied to the selected customer/vendor categories.')

    line_ids = fields.One2many('account.reconcile.model.line', 'model_id', copy=True)
    partner_mapping_line_ids = fields.One2many(string="Partner Mapping Lines",
                                               comodel_name='account.reconcile.model.partner.mapping',
                                               inverse_name='model_id',
                                               help="The mapping uses regular expressions.\n"
                                                    "- To Match the text at the beginning of the line (in label or notes), simply fill in your text.\n"
                                                    "- To Match the text anywhere (in label or notes), put your text between .*\n"
                                                    "  e.g: .*N°48748 abc123.*")
    past_months_limit = fields.Integer(
        string="Search Months Limit",
        default=18,
        tracking=True,
        help="Number of months in the past to consider entries from when applying this model.",
    )
    decimal_separator = fields.Char(
        default=lambda self: self.env['res.lang']._lang_get(self.env.user.lang).decimal_point,
        tracking=True,
        help="Every character that is nor a digit nor this separator will be removed from the matching string",
    )
    # used to decide if we should show the decimal separator for the regex matching field
    show_decimal_separator = fields.Boolean(compute='_compute_show_decimal_separator')
    number_entries = fields.Integer(string='Number of entries related to this model', compute='_compute_number_entries')

    def action_reconcile_stat(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        self._cr.execute('''
            SELECT ARRAY_AGG(DISTINCT move_id)
            FROM account_move_line
            WHERE reconcile_model_id = %s
        ''', [self.id])
        action.update({
            'context': {},
            'domain': [('id', 'in', self._cr.fetchone()[0])],
            'help': """<p class="o_view_nocontent_empty_folder">{}</p>""".format(_('This reconciliation model has created no entry so far')),
        })
        return action

    def _compute_number_entries(self):
        data = self.env['account.move.line']._read_group([('reconcile_model_id', 'in', self.ids)], ['reconcile_model_id'], 'reconcile_model_id')
        mapped_data = dict([(d['reconcile_model_id'][0], d['reconcile_model_id_count']) for d in data])
        for model in self:
            model.number_entries = mapped_data.get(model.id, 0)

    @api.depends('line_ids.amount_type')
    def _compute_show_decimal_separator(self):
        for record in self:
            record.show_decimal_separator = any(l.amount_type == 'regex' for l in record.line_ids)

    @api.depends('payment_tolerance_param', 'payment_tolerance_type')
    def _compute_payment_tolerance_param(self):
        for record in self:
            if record.payment_tolerance_type == 'percentage':
                record.payment_tolerance_param = min(100.0, max(0.0, record.payment_tolerance_param))
            else:
                record.payment_tolerance_param = max(0.0, record.payment_tolerance_param)

    @api.constrains('allow_payment_tolerance', 'payment_tolerance_param', 'payment_tolerance_type')
    def _check_payment_tolerance_param(self):
        for record in self:
            if record.allow_payment_tolerance:
                if record.payment_tolerance_type == 'percentage' and not 0 <= record.payment_tolerance_param <= 100:
                    raise ValidationError(_("A payment tolerance defined as a percentage should always be between 0 and 100"))
                elif record.payment_tolerance_type == 'fixed_amount' and record.payment_tolerance_param < 0:
                    raise ValidationError(_("A payment tolerance defined as an amount should always be higher than 0"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        if default.get('name'):
            return super(AccountReconcileModel, self).copy(default)
        name = _("%s (copy)", self.name)
        while self.env['account.reconcile.model'].search([('name', '=', name)], limit=1):
            name = _("%s (copy)", name)
        default['name'] = name
        return super(AccountReconcileModel, self).copy(default)

    ####################################################
    # RECONCILIATION PROCESS
    ####################################################

    def _apply_lines_for_bank_widget(self, residual_amount_currency, partner, st_line):
        """ Apply the reconciliation model lines to the statement line passed as parameter.

        :param residual_amount_currency:    The open balance of the statement line in the bank reconciliation widget
                                            expressed in the statement line currency.
        :param partner:                     The partner set on the wizard.
        :param st_line:                     The statement line processed by the bank reconciliation widget.
        :return:                            A list of python dictionaries (one per reconcile model line) representing
                                            the journal items to be created by the current reconcile model.
        """
        self.ensure_one()
        currency = st_line.foreign_currency_id or st_line.journal_id.currency_id or st_line.company_currency_id
        if currency.is_zero(residual_amount_currency):
            return []

        vals_list = []
        for line in self.line_ids:
            vals = line._apply_in_bank_widget(residual_amount_currency, partner, st_line)
            amount_currency = vals['amount_currency']

            if currency.is_zero(amount_currency):
                continue

            vals_list.append(vals)
            residual_amount_currency -= amount_currency

        return vals_list

    def _get_taxes_move_lines_dict(self, tax, base_line_dict):
        ''' Get move.lines dict (to be passed to the create()) corresponding to a tax.
        :param tax:             An account.tax record.
        :param base_line_dict:  A dict representing the move.line containing the base amount.
        :return: A list of dict representing move.lines to be created corresponding to the tax.
        '''
        self.ensure_one()
        balance = base_line_dict['balance']
        tax_type = tax.type_tax_use
        is_refund = (tax_type == 'sale' and balance > 0) or (tax_type == 'purchase' and balance < 0)

<<<<<<< HEAD
        tax_type = tax.type_tax_use
        is_refund = (tax_type == 'sale' and balance < 0) or (tax_type == 'purchase' and balance > 0)

        res = tax.compute_all(balance, is_refund=is_refund)
=======
        res = tax.compute_all(balance, is_refund=is_refund)

        if (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund):
            base_tags = self.env['account.account.tag'].browse(res['base_tags'])
            res['base_tags'] = self.env['account.move.line']._revert_signed_tags(base_tags).ids

            for tax_result in res['taxes']:
                tax_tags = self.env['account.account.tag'].browse(tax_result['tag_ids'])
                tax_result['tag_ids'] = self.env['account.move.line']._revert_signed_tags(tax_tags).ids
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

        new_aml_dicts = []
        for tax_res in res['taxes']:
            if self.company_id.currency_id.is_zero(tax_res['amount']):
                continue
            tax = self.env['account.tax'].browse(tax_res['id'])
            balance = tax_res['amount']
            name = ' '.join([x for x in [base_line_dict.get('name', ''), tax_res['name']] if x])
            new_aml_dicts.append({
                'account_id': tax_res['account_id'] or base_line_dict['account_id'],
                'journal_id': base_line_dict.get('journal_id', False),
                'name': name,
                'partner_id': base_line_dict.get('partner_id'),
                'balance': balance,
                'debit': balance > 0 and balance or 0,
                'credit': balance < 0 and -balance or 0,
<<<<<<< HEAD
                'analytic_distribution': tax.analytic and base_line_dict['analytic_distribution'],
=======
                'analytic_account_id': tax.analytic and base_line_dict['analytic_account_id'],
                'analytic_tag_ids': tax.analytic and base_line_dict['analytic_tag_ids'],
                'tax_exigible': tax_res['tax_exigibility'],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                'tax_repartition_line_id': tax_res['tax_repartition_line_id'],
                'tax_ids': [(6, 0, tax_res['tax_ids'])],
                'tax_tag_ids': [(6, 0, tax_res['tag_ids'])],
                'group_tax_id': tax_res['group'].id if tax_res['group'] else False,
                'currency_id': False,
                'reconcile_model_id': self.id,
            })

            # Handle price included taxes.
            base_balance = tax_res['base']
            base_line_dict.update({
                'balance': base_balance,
                'debit': base_balance > 0 and base_balance or 0,
                'credit': base_balance < 0 and -base_balance or 0,
            })

        base_line_dict['tax_tag_ids'] = [(6, 0, res['base_tags'])]
        return new_aml_dicts

    def _get_write_off_move_lines_dict(self, residual_balance, partner_id):
        ''' Get move.lines dict corresponding to the reconciliation model's write-off lines.
        :param residual_balance:    The residual balance of the account on the manual reconciliation widget.
        :return: A list of dict representing move.lines to be created corresponding to the write-off lines.
        '''
        self.ensure_one()

        if self.rule_type == 'invoice_matching' and (not self.allow_payment_tolerance or self.payment_tolerance_param == 0):
            return []

        currency = self.company_id.currency_id

        lines_vals_list = []
        for line in self.line_ids:
<<<<<<< HEAD
            if line.amount_type == 'percentage':
                balance = currency.round(residual_balance * (line.amount / 100.0))
            elif line.amount_type == 'fixed':
                balance = currency.round(line.amount * (1 if residual_balance > 0.0 else -1))

            if currency.is_zero(balance):
                continue
=======
            currency_id = st_line.currency_id or st_line.journal_id.currency_id or self.company_id.currency_id
            if not line.account_id or currency_id.is_zero(residual_balance):
                return []

            if line.amount_type == 'percentage':
                balance = residual_balance * (line.amount / 100.0)
            elif line.amount_type == "regex":
                match = re.search(line.amount_string, st_line.payment_ref)
                if match:
                    sign = 1 if residual_balance > 0.0 else -1
                    try:
                        extracted_match_group = re.sub(r'[^\d' + self.decimal_separator + ']', '', match.group(1))
                        extracted_balance = float(extracted_match_group.replace(self.decimal_separator, '.'))
                        balance = copysign(extracted_balance * sign, residual_balance)
                    except ValueError:
                        balance = 0
                else:
                    balance = 0
            else:
                balance = line.amount * (1 if residual_balance > 0.0 else -1)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

            writeoff_line = {
                'name': line.label,
                'balance': balance,
                'debit': balance > 0 and balance or 0,
                'credit': balance < 0 and -balance or 0,
                'account_id': line.account_id.id,
                'currency_id': currency.id,
                'analytic_distribution': line.analytic_distribution,
                'reconcile_model_id': self.id,
                'journal_id': line.journal_id.id,
                'tax_ids': [],
            }
            lines_vals_list.append(writeoff_line)

            residual_balance -= balance

            if line.tax_ids:
<<<<<<< HEAD
                taxes = line.tax_ids
                detected_fiscal_position = self.env['account.fiscal.position']._get_fiscal_position(self.env['res.partner'].browse(partner_id))
                if detected_fiscal_position:
                    taxes = detected_fiscal_position.map_tax(taxes)
                writeoff_line['tax_ids'] += [Command.set(taxes.ids)]
=======
                writeoff_line['tax_ids'] += [(6, None, line.tax_ids.ids)]
                tax = line.tax_ids
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
                # Multiple taxes with force_tax_included results in wrong computation, so we
                # only allow to set the force_tax_included field if we have one tax selected
                if line.force_tax_included:
                    taxes = taxes[0].with_context(force_price_include=True)
                tax_vals_list = self._get_taxes_move_lines_dict(taxes, writeoff_line)
                lines_vals_list += tax_vals_list
                if not line.force_tax_included:
                    for tax_line in tax_vals_list:
                        residual_balance -= tax_line['balance']

        return lines_vals_list

<<<<<<< HEAD
=======
    def _prepare_reconciliation(self, st_line, aml_ids=[], partner=None):
        ''' Prepare the reconciliation of the statement line with some counterpart line but
        also with some auto-generated write-off lines.

        The complexity of this method comes from the fact the reconciliation will be soft meaning
        it will be done only if the reconciliation will not trigger an error.
        For example, the reconciliation will be skipped if we need to create an open balance but we
        don't have a partner to get the receivable/payable account.

        This method works in two major steps. First, simulate the reconciliation of the account.move.line.
        Then, add some write-off lines depending the rule's fields.

        :param st_line: An account.bank.statement.line record.
        :param aml_ids: The ids of some account.move.line to reconcile.
        :param partner: An optional res.partner record. If not specified, fallback on the statement line's partner.
        :return: A list of dictionary to be passed to the account.bank.statement.line's 'reconcile' method.
        '''
        self.ensure_one()
        journal = st_line.journal_id
        company_currency = journal.company_id.currency_id
        foreign_currency = st_line.foreign_currency_id or journal.currency_id or company_currency

        liquidity_lines, suspense_lines, other_lines = st_line._seek_for_lines()

        if st_line.to_check:
            st_line_residual = -liquidity_lines.balance
            st_line_residual_currency = st_line._prepare_move_line_default_vals()[1]['amount_currency']
        elif suspense_lines.account_id.reconcile:
            st_line_residual = sum(suspense_lines.mapped('amount_residual'))
            st_line_residual_currency = sum(suspense_lines.mapped('amount_residual_currency'))
        else:
            st_line_residual = sum(suspense_lines.mapped('balance'))
            st_line_residual_currency = sum(suspense_lines.mapped('amount_currency'))

        has_full_write_off = any(rec_mod_line.amount == 100.0 for rec_mod_line in self.line_ids)

        lines_vals_list = []
        amls = self.env['account.move.line'].browse(aml_ids)
        st_line_residual_before = st_line_residual
        aml_total_residual = 0
        for aml in amls:
            aml_total_residual += aml.amount_residual

            if aml.balance * st_line_residual > 0:
                # Meaning they have the same signs, so they can't be reconciled together
                assigned_balance = -aml.amount_residual
                assigned_amount_currency = -aml.amount_residual_currency
            elif has_full_write_off:
                assigned_balance = -aml.amount_residual
                assigned_amount_currency = -aml.amount_residual_currency
                st_line_residual -= min(assigned_balance, st_line_residual, key=abs)
                st_line_residual_currency -= min(assigned_amount_currency, st_line_residual_currency, key=abs)
            else:
                assigned_balance = min(-aml.amount_residual, st_line_residual, key=abs)
                assigned_amount_currency = min(-aml.amount_residual_currency, st_line_residual_currency, key=abs)
                st_line_residual -= assigned_balance
                st_line_residual_currency -= assigned_amount_currency

            if aml.currency_id == foreign_currency:
                lines_vals_list.append({
                    'id': aml.id,
                    'balance': assigned_amount_currency,
                    'currency_id': foreign_currency.id,
                })
            else:
                lines_vals_list.append({
                    'id': aml.id,
                    'balance': assigned_balance,
                    'currency_id': company_currency.id,
                })

        write_off_amount = max(aml_total_residual, -st_line_residual_before, key=abs) + st_line_residual_before + st_line_residual

        reconciliation_overview, open_balance_vals = st_line._prepare_reconciliation(lines_vals_list)

        writeoff_vals_list = self._get_write_off_move_lines_dict(st_line, write_off_amount)

        for line_vals in writeoff_vals_list:
            st_line_residual -= st_line.company_currency_id.round(line_vals['balance'])
            line_vals['currency_id'] = st_line.company_currency_id.id

        # Check we have enough information to create an open balance.
        if open_balance_vals and not open_balance_vals.get('account_id'):
            return []

        return lines_vals_list + writeoff_vals_list

    def _prepare_widget_writeoff_vals(self, st_line_id, write_off_vals):
        counterpart_vals = st_line_id._prepare_counterpart_move_line_vals({
                **write_off_vals,
                'currency_id': st_line_id.company_id.currency_id.id,
            })
        return {
            **counterpart_vals,
            'balance': counterpart_vals['amount_currency'],
            'reconcile_model_id': self.id,
        }

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    ####################################################
    # RECONCILIATION CRITERIA
    ####################################################

    def _apply_rules(self, st_line, partner):
        ''' Apply criteria to get candidates for all reconciliation models.

        This function is called in enterprise by the reconciliation widget to match
        the statement line with the available candidates (using the reconciliation models).

        :param st_line: The statement line to match.
        :param partner: The partner to consider.
        :return:        A dict mapping each statement line id with:
            * aml_ids:          A list of account.move.line ids.
            * model:            An account.reconcile.model record (optional).
            * status:           'reconciled' if the lines has been already reconciled, 'write_off' if the write-off
                                must be applied on the statement line.
            * auto_reconcile:   A flag indicating if the match is enough significant to auto reconcile the candidates.
        '''
        available_models = self.filtered(lambda m: m.rule_type != 'writeoff_button').sorted()

<<<<<<< HEAD
=======
        # First associate with each rec models all the statement lines for which it is applicable
        lines_with_partner_per_model = defaultdict(lambda: [])
        for st_line in st_lines:

            # Statement lines created in old versions could have a residual amount of zero. In that case, don't try to
            # match anything.
            if not st_line.amount_residual:
                continue

            mapped_partner = (partner_map and partner_map.get(st_line.id) and self.env['res.partner'].browse(partner_map[st_line.id])) or st_line.partner_id

            for rec_model in available_models:
                partner = mapped_partner or rec_model._get_partner_from_mapping(st_line)

                if rec_model._is_applicable_for(st_line, partner):
                    lines_with_partner_per_model[rec_model].append((st_line, partner))

        # Execute only one SQL query for each model (for performance)
        matched_lines = self.env['account.bank.statement.line']
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        for rec_model in available_models:

            if not rec_model._is_applicable_for(st_line, partner):
                continue

            if rec_model.rule_type == 'invoice_matching':
                rules_map = rec_model._get_invoice_matching_rules_map()
                for rule_index in sorted(rules_map.keys()):
                    for rule_method in rules_map[rule_index]:
                        candidate_vals = rule_method(st_line, partner)
                        if not candidate_vals:
                            continue

                        if candidate_vals.get('amls'):
                            res = rec_model._get_invoice_matching_amls_result(st_line, partner, candidate_vals)
                            if res:
                                return {
                                    **res,
                                    'model': rec_model,
                                }
                        else:
                            return {
                                **candidate_vals,
                                'model': rec_model,
                            }

<<<<<<< HEAD
            elif rec_model.rule_type == 'writeoff_suggestion':
                return {
                    'model': rec_model,
                    'status': 'write_off',
                    'auto_reconcile': rec_model.auto_reconcile,
                }
        return {}
=======
                    if model_rslt:
                        # We inject the selected partner (possibly coming from the rec model)
                        model_rslt['partner']= partner

                        results[st_line.id] = model_rslt
                        reconciled_amls_ids |= new_reconciled_aml_ids
                        aml_ids_to_exclude |= new_treated_aml_ids
                        matched_lines += st_line

        return results
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def _is_applicable_for(self, st_line, partner):
        """ Returns true iff this reconciliation model can be used to search for matches
        for the provided statement line and partner.
        """
        self.ensure_one()

        # Filter on journals, amount nature, amount and partners
        # All the conditions defined in this block are non-match conditions.
        if ((self.match_journal_ids and st_line.move_id.journal_id not in self.match_journal_ids)
            or (self.match_nature == 'amount_received' and st_line.amount < 0)
            or (self.match_nature == 'amount_paid' and st_line.amount > 0)
            or (self.match_amount == 'lower' and abs(st_line.amount) >= self.match_amount_max)
            or (self.match_amount == 'greater' and abs(st_line.amount) <= self.match_amount_min)
            or (self.match_amount == 'between' and (abs(st_line.amount) > self.match_amount_max or abs(st_line.amount) < self.match_amount_min))
            or (self.match_partner and not partner)
            or (self.match_partner and self.match_partner_ids and partner not in self.match_partner_ids)
            or (self.match_partner and self.match_partner_category_ids and not (partner.category_id & self.match_partner_category_ids))
        ):
            return False

        # Filter on label, note and transaction_type
        for record, rule_field, record_field in [(st_line, 'label', 'payment_ref'), (st_line.move_id, 'note', 'narration'), (st_line, 'transaction_type', 'transaction_type')]:
            rule_term = (self['match_' + rule_field + '_param'] or '').lower()
            record_term = (record[record_field] or '').lower()

            # This defines non-match conditions
            if ((self['match_' + rule_field] == 'contains' and rule_term not in record_term)
                or (self['match_' + rule_field] == 'not_contains' and rule_term in record_term)
                or (self['match_' + rule_field] == 'match_regex' and not re.match(rule_term, record_term))
            ):
                return False

        return True

    def _get_invoice_matching_amls_domain(self, st_line, partner):
        aml_domain = st_line._get_default_amls_matching_domain()

        if st_line.amount > 0.0:
            aml_domain.append(('balance', '>', 0.0))
        else:
            aml_domain.append(('balance', '<', 0.0))

<<<<<<< HEAD
        currency = st_line.foreign_currency_id or st_line.currency_id
        if self.match_same_currency:
            aml_domain.append(('currency_id', '=', currency.id))

        if partner:
            aml_domain.append(('partner_id', '=', partner.id))

=======
        # On big databases, it is possible that some setups will create huge queries when trying to apply reconciliation models.
        # In such cases, this query might take a very long time to run, essentially eating up all the available CPU, and proof
        # impossible to kill, because of the type of operations ran by SQL. To alleviate that, we introduce the config parameter below,
        # which essentially allows cutting the list of statement lines to match into slices, and running the matching in multiple queries.
        # This way, we avoid server overload, giving the ability to kill the process if takes too long.
        slice_size = len(st_lines_with_partner)
        slice_size_param = self.env['ir.config_parameter'].sudo().get_param('account.reconcile_model_forced_slice_size')
        if slice_size_param:
            converted_param = int(slice_size_param)
            if converted_param > 0:
                slice_size = converted_param

        treatment_slices = []
        slice_start = 0
        while slice_start < len(st_lines_with_partner):
            slice_end = slice_start + slice_size
            treatment_slices.append(st_lines_with_partner[slice_start:slice_end])
            slice_start = slice_end

        treatment_map = {
            'invoice_matching': lambda rec_model, slice: rec_model._get_invoice_matching_query(slice, excluded_ids),
            'writeoff_suggestion': lambda rec_model, slice: rec_model._get_writeoff_suggestion_query(slice, excluded_ids),
        }
        rslt = defaultdict(lambda: [])
        for treatment_slice in treatment_slices:
            query_generator = treatment_map[self.rule_type]
            query, params = query_generator(self, treatment_slice)
            self._cr.execute(query, params)

            for candidate_dict in self._cr.dictfetchall():
                rslt[candidate_dict['id']].append(candidate_dict)

        return rslt

    def _get_invoice_matching_query(self, st_lines_with_partner, excluded_ids):
        ''' Returns the query applying the current invoice_matching reconciliation
        model to the provided statement lines.

        :param st_lines_with_partner: A list of tuples (statement_line, partner),
                                      associating each statement line to treate with
                                      the corresponding partner, given by the partner map
        :param excluded_ids:    Account.move.lines to exclude.
        :return:                (query, params)
        '''
        self.ensure_one()
        if self.rule_type != 'invoice_matching':
            raise UserError(_('Programmation Error: Can\'t call _get_invoice_matching_query() for different rules than \'invoice_matching\''))

        unaccent = get_unaccent_wrapper(self._cr)

        # N.B: 'communication_flag' is there to distinguish invoice matching through the number/reference
        # (higher priority) from invoice matching using the partner (lower priority).
        query = r'''
        SELECT
            st_line.id                          AS id,
            aml.id                              AS aml_id,
            aml.currency_id                     AS aml_currency_id,
            aml.date_maturity                   AS aml_date_maturity,
            aml.amount_residual                 AS aml_amount_residual,
            aml.amount_residual_currency        AS aml_amount_residual_currency,
            ''' + self._get_select_communication_flag() + r''' AS communication_flag,
            ''' + self._get_select_payment_reference_flag() + r''' AS payment_reference_flag
        FROM account_bank_statement_line st_line
        JOIN account_move st_line_move          ON st_line_move.id = st_line.move_id
        JOIN res_company company                ON company.id = st_line_move.company_id
        , account_move_line aml
        LEFT JOIN account_move move             ON move.id = aml.move_id AND move.state = 'posted'
        LEFT JOIN account_account account       ON account.id = aml.account_id
        LEFT JOIN res_partner aml_partner       ON aml.partner_id = aml_partner.id
        LEFT JOIN account_payment payment       ON payment.move_id = move.id
        WHERE
            aml.company_id = st_line_move.company_id
            AND move.state = 'posted'
            AND account.reconcile IS TRUE
            AND aml.reconciled IS FALSE
            AND (account.internal_type NOT IN ('receivable', 'payable') OR aml.payment_id IS NULL)
        '''

        # Add conditions to handle each of the statement lines we want to match
        st_lines_queries = []
        for st_line, partner in st_lines_with_partner:
            # In case we don't have any partner for this line, we try assigning one with the rule mapping
            if st_line.amount > 0:
                st_line_subquery = r"aml.balance > 0"
            else:
                st_line_subquery = r"aml.balance < 0"

            if self.match_same_currency:
                st_line_subquery += r" AND COALESCE(aml.currency_id, company.currency_id) = %s" % (st_line.foreign_currency_id.id or st_line.move_id.currency_id.id)

            if partner:
                st_line_subquery += r" AND aml.partner_id = %s" % partner.id
            else:
                st_line_fields_consideration = [
                    (self.match_text_location_label, 'st_line.payment_ref'),
                    (self.match_text_location_note, 'st_line_move.narration'),
                    (self.match_text_location_reference, 'st_line_move.ref'),
                ]

                no_partner_query = " OR ".join([
                    r"""
                        (
                            substring(REGEXP_REPLACE(""" + sql_field + """, '[^0-9\s]', '', 'g'), '\S(?:.*\S)*') != ''
                            AND
                            (
                                (""" + self._get_select_communication_flag() + """)
                                OR
                                (""" + self._get_select_payment_reference_flag() + """)
                            )
                        )
                        OR
                        (
                            /* We also match statement lines without partners with amls
                            whose partner's name's parts (splitting on space) are all present
                            within the payment_ref, in any order, with any characters between them. */

                            aml_partner.name IS NOT NULL
                            AND """ + unaccent(sql_field) + r""" ~* ('^' || (
                                SELECT string_agg(concat('(?=.*\m', chunk[1], '\M)'), '')
                                  FROM regexp_matches(""" + unaccent("aml_partner.name") + r""", '\w{3,}', 'g') AS chunk
                            ))
                        )
                    """
                    for consider_field, sql_field in st_line_fields_consideration
                    if consider_field
                ])

                if no_partner_query:
                    st_line_subquery += " AND " + no_partner_query

            st_lines_queries.append(r"st_line.id = %s AND (%s)" % (st_line.id, st_line_subquery))

        query += r" AND (%s) " % " OR ".join(st_lines_queries)

        params = {}

        # If this reconciliation model defines a past_months_limit, we add a condition
        # to the query to only search on move lines that are younger than this limit.
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        if self.past_months_limit:
            date_limit = fields.Date.context_today(self) - relativedelta(months=self.past_months_limit)
            aml_domain.append(('date', '>=', fields.Date.to_string(date_limit)))

        return aml_domain

    def _get_st_line_text_values_for_matching(self, st_line):
        """ Collect the strings that could be used on the statement line to perform some matching.

        :param st_line: The current statement line.
        :return: A list of strings.
        """
        self.ensure_one()
        allowed_fields = []
        if self.match_text_location_label:
            allowed_fields.append('payment_ref')
        if self.match_text_location_note:
            allowed_fields.append('narration')
        if self.match_text_location_reference:
            allowed_fields.append('ref')
        return st_line._get_st_line_strings_for_matching(allowed_fields=allowed_fields)

    def _get_invoice_matching_st_line_tokens(self, st_line):
        """ Parse the textual information from the statement line passed as parameter
        in order to extract from it the meaningful information in order to perform the matching.

        :param st_line: A statement line.
        :return:    A tuple of list of tokens, each one being a string.
                    The first element is a list of tokens you may match on numerical information.
                    The second element is a list of tokens you may match exactly.
        """
        st_line_text_values = self._get_st_line_text_values_for_matching(st_line)
        significant_token_size = 4
        numerical_tokens = []
        exact_tokens = []
        text_tokens = []
        for text_value in st_line_text_values:
            tokens = [
                ''.join(x for x in token if re.match(r'[0-9a-zA-Z\s]', x))
                for token in (text_value or '').split()
            ]

            # Numerical tokens
            for token in tokens:
                # The token is too short to be significant.
                if len(token) < significant_token_size:
                    continue

                text_tokens.append(token)

                formatted_token = ''.join(x for x in token if x.isdecimal())

                # The token is too short after formatting to be significant.
                if len(formatted_token) < significant_token_size:
                    continue

                numerical_tokens.append(formatted_token)

            # Exact tokens.
            if len(tokens) == 1:
                exact_tokens.append(tokens[0])
        return numerical_tokens, exact_tokens, text_tokens

    def _get_invoice_matching_amls_candidates(self, st_line, partner):
        """ Returns the match candidates for the 'invoice_matching' rule, with respect to the provided parameters.

        :param st_line: A statement line.
        :param partner: The partner associated to the statement line.
        """
        assert self.rule_type == 'invoice_matching'
        self.env['account.move'].flush_model()
        self.env['account.move.line'].flush_model()

        if self.matching_order == 'new_first':
            order_by = 'sub.date_maturity DESC, sub.date DESC, sub.id DESC'
        else:
            order_by = 'sub.date_maturity ASC, sub.date ASC, sub.id ASC'

        aml_domain = self._get_invoice_matching_amls_domain(st_line, partner)
        query = self.env['account.move.line']._where_calc(aml_domain)
        tables, where_clause, where_params = query.get_sql()

        sub_queries = []
        all_params = []
        numerical_tokens, exact_tokens, _text_tokens = self._get_invoice_matching_st_line_tokens(st_line)
        if numerical_tokens:
            for table_alias, field in (
                ('account_move_line', 'name'),
                ('account_move_line__move_id', 'name'),
                ('account_move_line__move_id', 'ref'),
            ):
                sub_queries.append(rf'''
                    SELECT
                        account_move_line.id,
                        account_move_line.date,
                        account_move_line.date_maturity,
                        UNNEST(
                            REGEXP_SPLIT_TO_ARRAY(
                                SUBSTRING(
                                    REGEXP_REPLACE({table_alias}.{field}, '[^0-9\s]', '', 'g'),
                                    '\S(?:.*\S)*'
                                ),
                                '\s+'
                            )
                        ) AS token
                    FROM {tables}
                    JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
                    WHERE {where_clause} AND {table_alias}.{field} IS NOT NULL
                ''')
                all_params += where_params

        if exact_tokens:
            for table_alias, field in (
                ('account_move_line', 'name'),
                ('account_move_line__move_id', 'name'),
                ('account_move_line__move_id', 'ref'),
            ):
                sub_queries.append(rf'''
                    SELECT
                        account_move_line.id,
                        account_move_line.date,
                        account_move_line.date_maturity,
                        {table_alias}.{field} AS token
                    FROM {tables}
                    JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
                    WHERE {where_clause} AND COALESCE({table_alias}.{field}, '') != ''
                ''')
                all_params += where_params

<<<<<<< HEAD
        if sub_queries:
            self._cr.execute(
                '''
                    SELECT
                        sub.id,
                        COUNT(*) AS nb_match
                    FROM (''' + ' UNION ALL '.join(sub_queries) + ''') AS sub
                    WHERE sub.token IN %s
                    GROUP BY sub.date_maturity, sub.date, sub.id
                    HAVING COUNT(*) > 0
                    ORDER BY nb_match DESC, ''' + order_by + '''
                ''',
                all_params + [tuple(numerical_tokens + exact_tokens)],
=======
        statement_compare = r"""(
                {move_field} IS NOT NULL AND substring(REGEXP_REPLACE({move_field}, '[^0-9\s]', '', 'g'), '\S(?:.*\S)*') != ''
                AND (
                    regexp_split_to_array(substring(REGEXP_REPLACE({move_field}, '[^0-9\s]', '', 'g'), '\S(?:.*\S)*'),'\s+')
                    && regexp_split_to_array(substring(REGEXP_REPLACE({st_ref}, '[^0-9\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                )
            )"""
        return " OR ".join(
            statement_compare.format(move_field=field, st_ref=st_ref)
            for field in ['aml.name', 'move.name', 'move.ref']
        )

    def _get_select_payment_reference_flag(self):
        # Determine a matching or not with the statement line communication using the move.payment_reference.
        st_ref_list = []
        if self.match_text_location_label:
            st_ref_list += ['st_line.payment_ref']
        if self.match_text_location_note:
            st_ref_list += ['st_line_move.narration']
        if self.match_text_location_reference:
            st_ref_list += ['st_line_move.ref']
        if not st_ref_list:
            return "FALSE"

        # payment_reference is not used on account.move for payments; ref is used instead
        return r'''((move.payment_reference IS NOT NULL OR (payment.id IS NOT NULL AND move.ref IS NOT NULL)) AND ({}))'''.format(
            ' OR '.join(
                rf"regexp_replace(CASE WHEN payment.id IS NULL THEN move.payment_reference ELSE move.ref END, '\s+', '', 'g') = regexp_replace({st_ref}, '\s+', '', 'g')"
                for st_ref in st_ref_list
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            )
            candidate_ids = [r[0] for r in self._cr.fetchall()]
            if candidate_ids:
                return {
                    'allow_auto_reconcile': True,
                    'amls': self.env['account.move.line'].browse(candidate_ids),
                }

        # Search without any matching based on textual information.
        if partner:

            if self.matching_order == 'new_first':
                order = 'date_maturity DESC, date DESC, id DESC'
            else:
                order = 'date_maturity ASC, date ASC, id ASC'

            amls = self.env['account.move.line'].search(aml_domain, order=order)
            if amls:
                return {
                    'allow_auto_reconcile': False,
                    'amls': amls,
                }

    def _get_invoice_matching_rules_map(self):
        """ Get a mapping <priority_order, rule> that could be overridden in others modules.

        :return: a mapping <priority_order, rule> where:
            * priority_order:   Defines in which order the rules will be evaluated, the lowest comes first.
                                This is extremely important since the algorithm stops when a rule returns some candidates.
            * rule:             Method taking <st_line, partner> as parameters and returning the candidates journal items found.
        """
        rules_map = defaultdict(list)
        rules_map[10].append(self._get_invoice_matching_amls_candidates)
        return rules_map

    def _get_partner_from_mapping(self, st_line):
        """Find partner with mapping defined on model.

        For invoice matching rules, matches the statement line against each
        regex defined in partner mapping, and returns the partner corresponding
        to the first one matching.

        :param st_line (Model<account.bank.statement.line>):
            The statement line that needs a partner to be found
        :return Model<res.partner>:
            The partner found from the mapping. Can be empty an empty recordset
            if there was nothing found from the mapping or if the function is
            not applicable.
        """
        self.ensure_one()

        if self.rule_type not in ('invoice_matching', 'writeoff_suggestion'):
            return self.env['res.partner']

        for partner_mapping in self.partner_mapping_line_ids:
            match_payment_ref = True
            if partner_mapping.payment_ref_regex:
                match_payment_ref = re.match(partner_mapping.payment_ref_regex, st_line.payment_ref) if st_line.payment_ref else False
            match_narration = True
            if partner_mapping.narration_regex:
                match_narration = re.match(
                    partner_mapping.narration_regex,
                    tools.html2plaintext(st_line.narration or '').rstrip(),
                    flags=re.DOTALL, # Ignore '/n' set by online sync.
                )

            if match_payment_ref and match_narration:
                return partner_mapping.partner_id
        return self.env['res.partner']

    def _get_invoice_matching_amls_result(self, st_line, partner, candidate_vals):
        def _create_result_dict(amls_values_list, status):
            if 'rejected' in status:
                return

            result = {'amls': self.env['account.move.line']}
            for aml_values in amls_values_list:
                result['amls'] |= aml_values['aml']

            if 'allow_write_off' in status and self.line_ids:
                result['status'] = 'write_off'

            if 'allow_auto_reconcile' in status and candidate_vals['allow_auto_reconcile'] and self.auto_reconcile:
                result['auto_reconcile'] = True

            return result

        st_line_currency = st_line.foreign_currency_id or st_line.currency_id
        st_line_amount = st_line._prepare_move_line_default_vals()[1]['amount_currency']
        sign = 1 if st_line_amount > 0.0 else -1

<<<<<<< HEAD
        amls = candidate_vals['amls']
        amls_values_list = []
        amls_with_epd_values_list = []
        same_currency_mode = amls.currency_id == st_line_currency
        for aml in amls:
            aml_values = {
                'aml': aml,
                'amount_residual': aml.amount_residual,
                'amount_residual_currency': aml.amount_residual_currency,
=======
        # We check the amount criteria of the reconciliation model, and select the
        # candidates if they pass the verification. Candidates from the first priority
        # level (even already selected) bypass this check, and are selected anyway.
        disable_bypass = self.env['ir.config_parameter'].sudo().get_param('account.disable_rec_models_bypass')
        if (not disable_bypass and priorities & {1,2}) or self._check_rule_propositions(st_line, candidates):
            rslt = {
                'model': self,
                'aml_ids': [candidate['aml_id'] for candidate in candidates],
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            }

            amls_values_list.append(aml_values)

<<<<<<< HEAD
            # Manage the early payment discount.
            if same_currency_mode \
                and aml.move_id.move_type in ('out_invoice', 'out_receipt', 'in_invoice', 'in_receipt') \
                and not aml.matched_debit_ids \
                and not aml.matched_credit_ids \
                and aml.discount_date \
                and st_line.date <= aml.discount_date:
=======
            # A write-off must be applied if there are some 'new' lines to propose.
            write_off_lines_vals = list(filter(lambda x: 'id' not in x, lines_vals_list))
            if not lines_vals_list or write_off_lines_vals:
                rslt['status'] = 'write_off'
                rslt['write_off_vals'] = write_off_lines_vals
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

                rate = abs(aml.amount_currency) / abs(aml.balance) if aml.balance else 1.0
                amls_with_epd_values_list.append({
                    **aml_values,
                    'amount_residual': st_line.company_currency_id.round(aml.discount_amount_currency / rate),
                    'amount_residual_currency': aml.discount_amount_currency,
                })
            else:
                amls_with_epd_values_list.append(aml_values)

<<<<<<< HEAD
        def match_batch_amls(amls_values_list):
            if not same_currency_mode:
                return None, []

            kepts_amls_values_list = []
            sum_amount_residual_currency = 0.0
            for aml_values in amls_values_list:

                if st_line_currency.compare_amounts(st_line_amount, -aml_values['amount_residual_currency']) == 0:
                    # Special case: the amounts are the same, submit the line directly.
                    return 'perfect', [aml_values]
=======
        # Statement line amount is equal to the total residual.
        if line_currency.is_zero(line_residual_after_reconciliation):
            return True
        residual_difference = line_residual - line_residual_after_reconciliation
        reconciled_percentage = 100 - abs(line_residual_after_reconciliation) / abs(residual_difference) * 100 if (residual_difference != 0) else 0
        return reconciled_percentage >= self.match_total_amount_param

    def _filter_candidates(self, candidates, aml_ids_to_exclude, reconciled_amls_ids):
        """ Sorts reconciliation candidates by priority and filters them so that only
        the most prioritary are kept.
        """
        candidates_by_priority = self._sort_reconciliation_candidates_by_priority(candidates, aml_ids_to_exclude, reconciled_amls_ids)

        # This can happen if the candidates were already reconciled at this point
        if not candidates_by_priority:
            return [], set()

        max_priority = min(candidates_by_priority.keys())
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

                if st_line_currency.compare_amounts(sign * (st_line_amount + sum_amount_residual_currency), 0.0) > 0:
                    # Here, we still have room for other candidates ; so we add the current one to the list we keep.
                    # Then, we continue iterating, even if there is no room anymore, just in case one of the following candidates
                    # is an exact match, which would then be preferred on the current candidates.
                    kepts_amls_values_list.append(aml_values)
                    sum_amount_residual_currency += aml_values['amount_residual_currency']

            if st_line_currency.is_zero(sign * (st_line_amount + sum_amount_residual_currency)):
                return 'perfect', kepts_amls_values_list
            elif kepts_amls_values_list:
                return 'partial', kepts_amls_values_list
            else:
                return None, []

        # Try to match a batch with the early payment feature. Only a perfect match is allowed.
        match_type, kepts_amls_values_list = match_batch_amls(amls_with_epd_values_list)
        if match_type != 'perfect':
            kepts_amls_values_list = []

        # Try to match the amls having the same currency as the statement line.
        if not kepts_amls_values_list:
            _match_type, kepts_amls_values_list = match_batch_amls(amls_values_list)

        # Try to match the whole candidates.
        if not kepts_amls_values_list:
            kepts_amls_values_list = amls_values_list

<<<<<<< HEAD
        # Try to match the amls having the same currency as the statement line.
        if kepts_amls_values_list:
            status = self._check_rule_propositions(st_line, kepts_amls_values_list)
            result = _create_result_dict(kepts_amls_values_list, status)
            if result:
                return result

    def _check_rule_propositions(self, st_line, amls_values_list):
        """ Check restrictions that can't be handled for each move.line separately.
        Note: Only used by models having a type equals to 'invoice_matching'.
        :param st_line:             The statement line.
        :param amls_values_list:    The candidates account.move.line as a list of dict:
            * aml:                          The record.
            * amount_residual:              The amount residual to consider.
            * amount_residual_currency:     The amount residual in foreign currency to consider.
        :return: A string representing what to do with the candidates:
            * rejected:             Reject candidates.
            * allow_write_off:      Allow to generate the write-off from the reconcile model lines if specified.
            * allow_auto_reconcile: Allow to automatically reconcile entries if 'auto_validate' is enabled.
        """
        self.ensure_one()

        if not self.allow_payment_tolerance:
            return {'allow_write_off', 'allow_auto_reconcile'}
=======
    def _get_writeoff_suggestion_rule_result(self, st_line, partner):
        # Create write-off lines.
        lines_vals_list = self._prepare_reconciliation(st_line, partner=partner)

        rslt = {
            'model': self,
            'status': 'write_off',
            'aml_ids': [],
            'write_off_vals': lines_vals_list,
        }

        # Process auto-reconciliation.
        if lines_vals_list and self.auto_reconcile:
            if not st_line.partner_id and partner:
                st_line.partner_id = partner
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

        st_line_currency = st_line.foreign_currency_id or st_line.currency_id
        st_line_amount_curr = st_line._prepare_move_line_default_vals()[1]['amount_currency']
        amls_amount_curr = sum(
            st_line._prepare_counterpart_amounts_using_st_line_rate(
                aml_values['aml'].currency_id,
                aml_values['amount_residual'],
                aml_values['amount_residual_currency'],
            )['amount_currency']
            for aml_values in amls_values_list
        )
        sign = 1 if st_line_amount_curr > 0.0 else -1
        amount_curr_after_rec = sign * (amls_amount_curr + st_line_amount_curr)

        # The statement line will be fully reconciled.
        if st_line_currency.is_zero(amount_curr_after_rec):
            return {'allow_auto_reconcile'}

        # The payment amount is higher than the sum of invoices.
        # In that case, don't check the tolerance and don't try to generate any write-off.
        if amount_curr_after_rec > 0.0:
            return {'allow_auto_reconcile'}

        # No tolerance, reject the candidates.
        if self.payment_tolerance_param == 0:
            return {'rejected'}

        # If the tolerance is expressed as a fixed amount, check the residual payment amount doesn't exceed the
        # tolerance.
        if self.payment_tolerance_type == 'fixed_amount' and -amount_curr_after_rec <= self.payment_tolerance_param:
            return {'allow_write_off', 'allow_auto_reconcile'}

        # The tolerance is expressed as a percentage between 0 and 100.0.
        reconciled_percentage_left = (abs(amount_curr_after_rec / amls_amount_curr)) * 100.0
        if self.payment_tolerance_type == 'percentage' and reconciled_percentage_left <= self.payment_tolerance_param:
            return {'allow_write_off', 'allow_auto_reconcile'}

        return {'rejected'}
