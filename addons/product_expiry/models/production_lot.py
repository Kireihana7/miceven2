# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from odoo import api, fields, models, SUPERUSER_ID, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    use_expiration_date = fields.Boolean(
        string='Use Expiration Date', related='product_id.use_expiration_date')
    expiration_date = fields.Datetime(
        string='Expiration Date', compute='_compute_expiration_date', store=True, readonly=False,
        help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.')
    use_date = fields.Datetime(string='Best before Date', compute='_compute_dates', store=True, readonly=False,
        help='This is the date on which the goods with this Serial Number start deteriorating, without being dangerous yet.')
    removal_date = fields.Datetime(string='Removal Date', compute='_compute_dates', store=True, readonly=False,
        help='This is the date on which the goods with this Serial Number should be removed from the stock. This date will be used in FEFO removal strategy.')
    alert_date = fields.Datetime(string='Alert Date', compute='_compute_dates', store=True, readonly=False,
        help='Date to determine the expired lots and serial numbers using the filter "Expiration Alerts".')
    product_expiry_alert = fields.Boolean(compute='_compute_product_expiry_alert', help="The Expiration Date has been reached.")
    product_expiry_reminded = fields.Boolean(string="Expiry has been reminded")

    @api.depends('expiration_date')
    def _compute_product_expiry_alert(self):
        current_date = fields.Datetime.now()
        for lot in self:
            if lot.expiration_date:
                lot.product_expiry_alert = lot.expiration_date <= current_date
            else:
                lot.product_expiry_alert = False

    @api.depends('product_id')
    def _compute_expiration_date(self):
        self.expiration_date = False
        for lot in self:
            if lot.product_id.use_expiration_date and not lot.expiration_date:
                duration = lot.product_id.product_tmpl_id.expiration_time
                lot.expiration_date = datetime.datetime.now() + datetime.timedelta(days=duration)

<<<<<<< HEAD
    @api.depends('product_id', 'expiration_date')
    def _compute_dates(self):
        for lot in self:
            if not lot.product_id.use_expiration_date:
                lot.use_date = False
                lot.removal_date = False
                lot.alert_date = False
            elif lot.expiration_date:
                # when create
                if lot.product_id != lot._origin.product_id or \
                   (not lot.use_date and not lot.removal_date and not lot.alert_date) or \
                   (lot.expiration_date and not lot._origin.expiration_date):
                    product_tmpl = lot.product_id.product_tmpl_id
                    lot.use_date = lot.expiration_date - datetime.timedelta(days=product_tmpl.use_time)
                    lot.removal_date = lot.expiration_date - datetime.timedelta(days=product_tmpl.removal_time)
                    lot.alert_date = lot.expiration_date - datetime.timedelta(days=product_tmpl.alert_time)
                # when change
                elif lot._origin.expiration_date:
                    time_delta = lot.expiration_date - lot._origin.expiration_date
                    lot.use_date = lot._origin.use_date and lot._origin.use_date + time_delta
                    lot.removal_date = lot._origin.removal_date and lot._origin.removal_date + time_delta
                    lot.alert_date = lot._origin.alert_date and lot._origin.alert_date + time_delta
=======
    # Assign dates according to products data
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            dates = self._get_dates(vals.get('product_id') or self.env.context.get('default_product_id'))
            for d in dates:
                if not vals.get(d):
                    vals[d] = dates[d]
        return super().create(vals_list)

    @api.onchange('expiration_date')
    def _onchange_expiration_date(self):
        if not self._origin or not (self.expiration_date and self._origin.expiration_date):
            return
        time_delta = self.expiration_date - self._origin.expiration_date
        # As we compare expiration_date with _origin.expiration_date, we need to
        # use `_get_date_values` with _origin to keep a stability in the values.
        # Otherwise it will recompute from the updated values if the user calls
        # this onchange multiple times without save between each onchange.
        vals = self._origin._get_date_values(time_delta, self.expiration_date)
        self.update(vals)

    @api.onchange('product_id')
    def _onchange_product(self):
        dates_dict = self._get_dates()
        for field, value in dates_dict.items():
            setattr(self, field, value)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    @api.model
    def _alert_date_exceeded(self):
        """Log an activity on internally stored lots whose alert_date has been reached.

        No further activity will be generated on lots whose alert_date
        has already been reached (even if the alert_date is changed).
        """
        alert_lots = self.env['stock.lot'].search([
            ('alert_date', '<=', fields.Date.today()),
            ('product_expiry_reminded', '=', False)])

        lot_stock_quants = self.env['stock.quant'].search([
            ('lot_id', 'in', alert_lots.ids),
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal')])
        alert_lots = lot_stock_quants.mapped('lot_id')

        for lot in alert_lots:
            lot.activity_schedule(
                'product_expiry.mail_activity_type_alert_date_reached',
                user_id=lot.product_id.with_company(lot.company_id).responsible_id.id or lot.product_id.responsible_id.id or SUPERUSER_ID,
                note=_("The alert date has been reached for this lot/serial number")
            )
        alert_lots.write({
            'product_expiry_reminded': True
        })

<<<<<<< HEAD
=======
    def _update_date_values(self, new_date):
        if new_date:
            time_delta = new_date - (self.expiration_date or fields.Datetime.now())
            vals = self._get_date_values(time_delta, new_date)
            vals['expiration_date'] = new_date
            self.write(vals)

    def _get_date_values(self, time_delta, new_date=False):
        ''' Return a dict with different date values updated depending of the
        time_delta. Used in the onchange of `expiration_date` and when user
        defines a date at the receipt. '''
        vals = {
            'use_date': self.use_date and (self.use_date + time_delta) or new_date,
            'removal_date': self.removal_date and (self.removal_date + time_delta) or new_date,
            'alert_date': self.alert_date and (self.alert_date + time_delta) or new_date,
        }
        return vals

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        super(ProcurementGroup, self)._run_scheduler_tasks(use_new_cursor=use_new_cursor, company_id=company_id)
        self.env['stock.lot']._alert_date_exceeded()
        if use_new_cursor:
            self.env.cr.commit()
